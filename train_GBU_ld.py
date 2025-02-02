import torch
import torch.nn.functional as F
from torch.autograd import Variable
import torch.autograd as autograd
import torch.optim as optim
import torch.nn.init as init
from firelab.config import Config
from sklearn.preprocessing import normalize

from termcolor import cprint
from time import gmtime, strftime
import numpy as np
import argparse
import os
import glob
import random
import json

from dataset_GBU import FeatDataLayer, DATA_LOADER
from models import _netD, _netG_att, _param
from losses.gan_losses import compute_gradient_penalty, compute_centroid_loss
from losses.prototype_loss import compute_prototype_loss
from losses.rw_loss_low_dimension import compute_rw_real_loss, compute_rw_imitative_loss, compute_rw_creative_loss
from losses.ausuc import compute_ausuc

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', default='CUB', help='FLO')
parser.add_argument('--dataroot', default='data/GBU/', help='path to dataset')
parser.add_argument('--matdataset', default=True, help='Data in matlab format')
parser.add_argument('--image_embedding', default='res101')
parser.add_argument('--class_embedding', default='att')
parser.add_argument('--preprocessing', action='store_true', default=True,
                    help='enbale MinMaxScaler on visual features')
parser.add_argument('--standardization', action='store_true', default=False)
parser.add_argument('--validation', action='store_true', default=False, help='enable cross validation mode')
# parser.add_argument('--splitmode', default='', type=str, help='Dummy argument for compatibility with train.py. Do not use it here.')
parser.add_argument('--gpu', default='0', type=str, help='index of GPU to use')
parser.add_argument('--exp_idx', default='', type=str, help='exp idx')
parser.add_argument('--manualSeed', type=int, help='manual seed')
parser.add_argument('--resume',  type=str, help='the model to resume')

parser.add_argument('--disp_interval', type=int, default=20)
parser.add_argument('--save_interval', type=int, default=200)
parser.add_argument('--evl_interval',  type=int, default=40)
parser.add_argument('--rw_config_path', default='rw_config.yml', help='Path to RW loss configuration file')
parser.add_argument('--num_iterations', default=3000, type=int, help='For how many iterations to run.')

parser.add_argument('--exp_name', default='Reproduce', type=str, help='Experiment Name')

opt, _ = parser.parse_known_args()
print('Running parameters:')
print(json.dumps(vars(opt), indent=4, separators=(',', ':')))

rw_config = Config.load(opt.rw_config_path, frozen=False)
rw_config_cli = Config.read_from_cli(config_arg_prefix='--rw_config.')
rw_config = rw_config.overwrite(rw_config_cli)
rw_config.freeze()
print('<=========== Random Walk config ===========>')
print(rw_config)

# os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpu

""" hyper-parameter  """
opt.GP_LAMBDA = 10    # Gradient penalty lambda
opt.CENT_LAMBDA  = 5
opt.REG_W_LAMBDA = 0.001
opt.Adv_LAMBDA = 1

opt.z_dim = rw_config.z_dim
opt.lr = rw_config.lr
opt.batchsize = 1024  # 512

""" hyper-parameter for testing"""
opt.nSample = 60  # number of fake feature for each class
opt.Knn = 20      # knn: the value of K


if opt.manualSeed is None:
    opt.manualSeed = 42
print("Random Seed: ", opt.manualSeed)
random.seed(opt.manualSeed)
torch.manual_seed(opt.manualSeed)
torch.cuda.manual_seed_all(opt.manualSeed)


def train():
    param = _param()
    dataset = DATA_LOADER(opt)
    param.X_dim = dataset.feature_dim

    data_layer = FeatDataLayer(dataset.train_label.numpy(), dataset.train_feature.numpy(), opt)
    result = Result()
    result_gzsl = Result()

    netG = _netG_att(opt, dataset.text_dim, dataset.feature_dim).cuda()
    netG.apply(weights_init)
    print(netG)
    netD = _netD(dataset.train_cls_num, dataset.feature_dim).cuda()
    netD.apply(weights_init)
    print(netD)

    exp_info = 'GBU_{}_{}'.format(opt.dataset, opt.exp_name)
    exp_params = rw_config.compute_hash()

    out_dir  = 'out/{:s}'.format(exp_info)
    out_subdir = 'out/{:s}/{:s}'.format(exp_info, exp_params)
    if not os.path.exists('out'):
        os.mkdir('out')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    if not os.path.exists(out_subdir):
        os.mkdir(out_subdir)

    cprint(" The output dictionary is {}".format(out_subdir), 'red')
    log_dir = out_subdir + '/log_{:s}_{}.txt'.format(exp_info, opt.exp_idx)
    with open(log_dir, 'w') as f:
        f.write('Training Start:')
        f.write(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()) + '\n')

    start_step = 0

    if opt.resume:
        if os.path.isfile(opt.resume):
            print("=> loading checkpoint '{}'".format(opt.resume))
            checkpoint = torch.load(opt.resume)
            netG.load_state_dict(checkpoint['state_dict_G'])
            netD.load_state_dict(checkpoint['state_dict_D'])
            start_step = checkpoint['it']
            print(checkpoint['log'])
        else:
            print("=> no checkpoint found at '{}'".format(opt.resume))
    nets = [netG, netD]

    tr_cls_centroid = Variable(torch.from_numpy(dataset.tr_cls_centroid.astype('float32'))).cuda()
    optimizerD = optim.Adam(netD.parameters(), lr=opt.lr, betas=(0.5, 0.9))
    optimizerG = optim.Adam(netG.parameters(), lr=opt.lr, betas=(0.5, 0.9))

    for it in range(start_step, opt.num_iterations + 1):
        # Creative Loss
        blobs = data_layer.forward()
        labels = blobs['labels'].astype(int)
        new_class_labels = Variable(torch.from_numpy(np.ones_like(labels) * dataset.train_cls_num)).cuda()
        text_feat_1 = np.array([dataset.train_text_feature[i, :] for i in labels])
        text_feat_2 = np.array([dataset.train_text_feature[i, :] for i in labels])
        np.random.shuffle(text_feat_1)  # Shuffle both features to guarantee different permutations
        np.random.shuffle(text_feat_2)
        alpha = (np.random.random(len(labels)) * (.8 - .2)) + .2

        text_feat_mean = np.multiply(alpha, text_feat_1.transpose())
        text_feat_mean += np.multiply(1. - alpha, text_feat_2.transpose())
        text_feat_mean = text_feat_mean.transpose()
        text_feat_mean = normalize(text_feat_mean, norm='l2', axis=1)
        text_feat_Creative = Variable(torch.from_numpy(text_feat_mean.astype('float32'))).cuda()
        z_creative = Variable(torch.randn(opt.batchsize, opt.z_dim)).cuda()
        G_creative_sample = netG(z_creative, text_feat_Creative)

        """ Discriminator """
        for _ in range(5):
            blobs = data_layer.forward()
            feat_data = blobs['data']             # image data
            labels = blobs['labels'].astype(int)  # class labels
            text_feat = np.array([ dataset.train_text_feature[i,:] for i in labels])
            text_feat = Variable(torch.from_numpy(text_feat.astype('float32'))).cuda()
            X = Variable(torch.from_numpy(feat_data)).cuda()
            y_true = Variable(torch.from_numpy(labels.astype('int'))).cuda()
            z = Variable(torch.randn(opt.batchsize, opt.z_dim)).cuda()

            # GAN's D loss
            D_real, C_real = netD(X)
            D_loss_real = torch.mean(D_real)
            C_loss_real = F.cross_entropy(C_real, y_true)
            DC_loss = opt.Adv_LAMBDA *(-D_loss_real + C_loss_real)
            DC_loss.backward()

            # GAN's D loss
            G_sample = netG(z, text_feat).detach()
            D_fake, C_fake = netD(G_sample)
            D_loss_fake = torch.mean(D_fake)

            C_loss_fake = F.cross_entropy(C_fake, y_true)
            DC_loss = opt.Adv_LAMBDA *(D_loss_fake + C_loss_fake)
            DC_loss.backward()

            # train with gradient penalty (WGAN_GP)
            grad_penalty = opt.Adv_LAMBDA * calc_gradient_penalty(netD, X.data, G_sample.data)
            grad_penalty.backward()

            # # Imitative fake RW loss for Discriminator
            # discr_rw_imitative_walker_loss, discr_rw_imitative_visit_loss = compute_rw_imitative_loss(rw_config, data_layer, dataset, netD, netG)
            # discr_rw_imitative_loss = discr_rw_imitative_walker_loss + rw_config.loss_weights.get('visit_loss', 1.0) * discr_rw_imitative_visit_loss
            # discr_rw_imitative_loss = rw_config.loss_weights.discr.imitative * discr_rw_imitative_loss
            # discr_rw_imitative_loss.backward()
            #
            # # Imitative real RW loss for Discriminator
            # discr_rw_real_walker_loss, discr_rw_real_visit_loss = compute_rw_real_loss(rw_config, data_layer, dataset, netD, netG)
            # discr_rw_real_loss = discr_rw_real_walker_loss + rw_config.loss_weights.get('visit_loss', 1.0) * discr_rw_real_visit_loss
            # discr_rw_real_loss = rw_config.loss_weights.discr.real * discr_rw_real_loss
            # discr_rw_real_loss.backward()

            Wasserstein_D = D_loss_real - D_loss_fake
            optimizerD.step()
            reset_grad(nets)

        """ Generator """
        for _ in range(1):
            blobs = data_layer.forward()
            feat_data = blobs['data']  # image data
            labels = blobs['labels'].astype(int)  # class labels
            text_feat = np.array([dataset.train_text_feature[i, :] for i in labels])
            text_feat = Variable(torch.from_numpy(text_feat.astype('float32'))).cuda()

            X = Variable(torch.from_numpy(feat_data)).cuda()
            y_true = Variable(torch.from_numpy(labels.astype('int'))).cuda()
            z = Variable(torch.randn(opt.batchsize, opt.z_dim)).cuda()

            G_sample = netG(z, text_feat)
            D_fake, C_fake = netD(G_sample)
            _,      C_real = netD(X)

            # GAN's G loss
            G_loss = torch.mean(D_fake)
            # Auxiliary classification loss
            C_loss = (F.cross_entropy(C_real, y_true) + F.cross_entropy(C_fake, y_true)) / 2
            GC_loss = opt.Adv_LAMBDA *(-G_loss + C_loss)

            # Centroid loss
            Euclidean_loss = Variable(torch.Tensor([0.0])).cuda()
            if opt.REG_W_LAMBDA != 0:
                for i in range(dataset.train_cls_num):
                    sample_idx = (y_true == i).data.nonzero().squeeze()
                    if sample_idx.numel() == 0:
                        Euclidean_loss += 0.0
                    else:
                        G_sample_cls = G_sample[sample_idx, :]
                        Euclidean_loss += (G_sample_cls.mean(dim=0) - tr_cls_centroid[i]).pow(2).sum().sqrt()
                Euclidean_loss *= 1.0/dataset.train_cls_num * opt.CENT_LAMBDA

            # ||W||_2 regularization
            reg_loss = Variable(torch.Tensor([0.0])).cuda()
            if opt.REG_W_LAMBDA != 0:
                for name, p in netG.named_parameters():
                    if 'weight' in name:
                        reg_loss += p.pow(2).sum()
                reg_loss.mul_(opt.REG_W_LAMBDA)

            # # Imitative RW loss for Generator
            # gen_rw_imitative_walker_loss, gen_rw_imitative_visit_loss = compute_rw_imitative_loss(rw_config, data_layer, dataset, netD, netG)
            # gen_rw_imitative_loss = gen_rw_imitative_walker_loss + rw_config.loss_weights.get('visit_loss', 1.0) * gen_rw_imitative_visit_loss
            # gen_rw_imitative_loss = rw_config.loss_weights.gen.imitative * gen_rw_imitative_loss

            # Creative RW loss for Generator
            gen_rw_creative_walker_loss, gen_rw_creative_visit_loss = compute_rw_creative_loss(rw_config, data_layer, dataset, netD, G_creative_sample, netG)
            gen_rw_creative_loss = gen_rw_creative_walker_loss + rw_config.loss_weights.get('visit_loss', 1.0) * gen_rw_creative_visit_loss
            gen_rw_creative_loss = rw_config.loss_weights.gen.creative * gen_rw_creative_loss

            all_loss = GC_loss + Euclidean_loss + reg_loss + gen_rw_creative_loss

            all_loss.backward()
            optimizerG.step()
            reset_grad(nets)

        if it % opt.disp_interval == 0 and it:
            acc_real = (np.argmax(C_real.data.cpu().numpy(), axis=1) == y_true.data.cpu().numpy()).sum() / float(y_true.data.size()[0])
            acc_fake = (np.argmax(C_fake.data.cpu().numpy(), axis=1) == y_true.data.cpu().numpy()).sum() / float(y_true.data.size()[0])

            log_text = 'Iter-{}; Was_D: {:.3f}; Euc_ls: {:.3f}; reg_ls: {:.3f}; G_loss: {:.3f}; D_loss_real: {:.3f};' \
                       ' D_loss_fake: {:.3f}; rl: {:.2f}%; fk: {:.2f}%'\
                        .format(it, Wasserstein_D.item(),  Euclidean_loss.item(), reg_loss.item(),
                                G_loss.item(), D_loss_real.item(), D_loss_fake.item(), acc_real * 100, acc_fake * 100)
            print(log_text)
            with open(log_dir, 'a') as f:
                f.write(log_text+'\n')
        else:
            log_text = ''

        if it % opt.evl_interval == 0 and it >= 100:
            netG.eval()
            eval_fakefeat_test(it, netG, dataset, param, result)
            if result.save_model:
                files2remove = glob.glob(out_subdir + '/Best_model_ZSL_*')
                for _i in files2remove:
                    os.remove(_i)
                # best_acc = result.acc_list[-1]
                save_model(it, netG, netD, opt.manualSeed, log_text,
                           out_subdir + '/Best_model_ZSL_Acc_{:.2f}.tar'.format(result.acc_list[-1]))

            eval_fakefeat_test_gzsl(it, netG, dataset, param, result_gzsl)
            if result.save_model:
                files2remove = glob.glob(out_subdir + '/Best_model_GZSL_*')
                for _i in files2remove:
                    os.remove(_i)
                # best_acc_gzsl = result.acc_list[-1]
                save_model(it, netG, netD, opt.manualSeed, log_text,
                           out_subdir + '/Best_model_GZSL_H_{:.2f}_S_{:.2f}_U_{:.2f}.tar'.format(result_gzsl.best_acc,
                                                                                                 result_gzsl.best_acc_S_T,
                                                                                                 result_gzsl.best_acc_U_T))

            netG.train()

        if it % opt.save_interval == 0 and it:
            save_model(it, netG, netD, opt.manualSeed, log_text,
                       out_subdir + '/Iter_{:d}.tar'.format(it))
            cprint('Save model to ' + out_subdir + '/Iter_{:d}.tar'.format(it), 'red')


def save_model(it, netG, netD, random_seed, log, fout):
    torch.save({
        'it': it + 1,
        'state_dict_G': netG.state_dict(),
        'state_dict_D': netD.state_dict(),
        'random_seed': random_seed,
        'log': log,
    }, fout)


def eval_fakefeat_test(it, netG, dataset, param, result):
    gen_feat = np.zeros([0, param.X_dim])
    for i in range(dataset.test_cls_num):
        text_feat = np.tile(dataset.test_text_feature[i].astype('float32'), (opt.nSample, 1))
        text_feat = Variable(torch.from_numpy(text_feat)).cuda()
        z = Variable(torch.randn(opt.nSample, opt.z_dim)).cuda()
        G_sample = netG(z, text_feat)
        gen_feat = np.vstack((gen_feat, G_sample.data.cpu().numpy()))

    from sklearn.metrics.pairwise import cosine_similarity
    # cosince predict K-nearest Neighbor
    sim = cosine_similarity(dataset.test_unseen_feature, gen_feat)
    idx_mat = np.argsort(-1 * sim, axis=1)
    label_mat = (idx_mat[:, 0:opt.Knn] / opt.nSample).astype(int)
    preds = np.zeros(label_mat.shape[0])
    for i in range(label_mat.shape[0]):
        (values, counts) = np.unique(label_mat[i], return_counts=True)
        preds[i] = values[np.argmax(counts)]

    # produce MCA
    label_T = np.asarray(dataset.test_unseen_label)
    acc = np.zeros(label_T.max() + 1)
    for i in range(label_T.max() + 1):
        acc[i] = (preds[label_T == i] == i).mean()
    acc = acc.mean() * 100

    result.acc_list += [acc]
    result.iter_list += [it]
    result.save_model = False
    if acc > result.best_acc:
        result.best_acc = acc
        result.best_iter = it
        result.save_model = True
    print("{}nn Classifer: ".format(opt.Knn))
    print("Accuracy is {:.2f}%".format(acc))


def eval_fakefeat_test_gzsl(it, netG, dataset, param, result):
    from sklearn.metrics.pairwise import cosine_similarity
    gen_feat_train_cls = np.zeros([0, param.X_dim])
    for i in range(dataset.train_cls_num):
        text_feat = np.tile(dataset.train_text_feature[i].astype('float32'), (opt.nSample, 1))
        text_feat = Variable(torch.from_numpy(text_feat)).cuda()
        z = Variable(torch.randn(opt.nSample, opt.z_dim)).cuda()
        G_sample = netG(z, text_feat)
        gen_feat_train_cls = np.vstack((gen_feat_train_cls, G_sample.data.cpu().numpy()))

    gen_feat_test_cls = np.zeros([0, param.X_dim])
    for i in range(dataset.test_cls_num):
        text_feat = np.tile(dataset.test_text_feature[i].astype('float32'), (opt.nSample, 1))
        text_feat = Variable(torch.from_numpy(text_feat)).cuda()
        z = Variable(torch.randn(opt.nSample, opt.z_dim)).cuda()
        G_sample = netG(z, text_feat)
        gen_feat_test_cls = np.vstack((gen_feat_test_cls, G_sample.data.cpu().numpy()))

    """  S -> T
    """
    sim = cosine_similarity(dataset.test_seen_feature, np.vstack((gen_feat_train_cls, gen_feat_test_cls)))
    idx_mat = np.argsort(-1 * sim, axis=1)
    label_mat = (idx_mat[:, 0:opt.Knn] / opt.nSample).astype(int)
    preds = np.zeros(label_mat.shape[0])
    for i in range(label_mat.shape[0]):
        (values, counts) = np.unique(label_mat[i], return_counts=True)
        preds[i] = values[np.argmax(counts)]
    # produce MCA
    label_T = np.asarray(dataset.test_seen_label)
    acc = np.zeros(label_T.max() + 1)
    for i in range(label_T.max() + 1):
        acc[i] = (preds[label_T == i] == i).mean()
    acc_S_T = acc.mean() * 100

    """  U -> T
    """
    sim = cosine_similarity(dataset.test_unseen_feature, np.vstack((gen_feat_test_cls, gen_feat_train_cls)))
    idx_mat = np.argsort(-1 * sim, axis=1)
    label_mat = (idx_mat[:, 0:opt.Knn] / opt.nSample).astype(int)
    preds = np.zeros(label_mat.shape[0])
    for i in range(label_mat.shape[0]):
        (values, counts) = np.unique(label_mat[i], return_counts=True)
        preds[i] = values[np.argmax(counts)]
    # produce MCA
    label_T = np.asarray(dataset.test_unseen_label)
    acc = np.zeros(label_T.max() + 1)
    for i in range(label_T.max() + 1):
        acc[i] = (preds[label_T == i] == i).mean()
    acc_U_T = acc.mean() * 100
    acc = (2 * acc_S_T * acc_U_T) / (acc_S_T + acc_U_T)

    result.acc_list += [acc]
    result.iter_list += [it]
    result.save_model = False
    if acc > result.best_acc:
        result.best_acc = acc
        result.best_iter = it
        result.best_acc_S_T = acc_S_T
        result.best_acc_U_T = acc_U_T
        result.save_model = True

    print("H {:.2f}%  S->T {:.2f}%  U->T {:.2f}%  ".format(acc, acc_S_T, acc_U_T))


class Result(object):
    def __init__(self):
        self.best_acc = 0.0
        self.best_iter = 0.0
        self.best_acc_S_T = 0.0
        self.best_acc_U_T = 0.0
        self.acc_list = []
        self.iter_list = []


def weights_init(m):
    classname = m.__class__.__name__
    if 'Linear' in classname:
        init.xavier_normal(m.weight.data)
        init.constant(m.bias, 0.0)


def reset_grad(nets):
    for net in nets:
        net.zero_grad()


def label2mat(labels, y_dim):
    c = np.zeros([labels.shape[0], y_dim])
    for idx, d in enumerate(labels):
        c[idx, d] = 1
    return c


def calc_gradient_penalty(netD, real_data, fake_data):
    alpha = torch.rand(opt.batchsize, 1)
    alpha = alpha.expand(real_data.size())
    alpha = alpha.cuda()

    interpolates = alpha * real_data + ((1 - alpha) * fake_data)
    interpolates = interpolates.cuda()
    interpolates = autograd.Variable(interpolates, requires_grad=True)

    disc_interpolates, _ = netD(interpolates)

    gradients = autograd.grad(outputs=disc_interpolates, inputs=interpolates,
                              grad_outputs=torch.ones(disc_interpolates.size()).cuda(),
                              create_graph=True, retain_graph=True, only_inputs=True)[0]
    gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean() * opt.GP_LAMBDA
    return gradient_penalty


if __name__ == "__main__":
    train()
