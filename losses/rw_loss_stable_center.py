from typing import List
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from firelab.config import Config


def compute_random_walk_loss(
        config: Config, discriminator: nn.Module, proto_imgs: Tensor,
        proto_img_labels: List[int], point_imgs: List[int], target_dist: str,
        point_img_labels: List[int]=None, step_weights: Tensor=None) -> Tensor:
    """
    Computes Random Walk loss for the generated images
    """
    if not point_img_labels is None:
        # We should filter out those prototypes that are not among points
        allowed_labels = set(np.unique(point_img_labels).tolist())
        allowed_proto_img_idx = [i for i, y in enumerate(proto_img_labels.cpu().tolist()) if y in allowed_labels]
        # print(f'shape of allowed_proto_img_idx is {len(allowed_proto_img_idx)}') # 1600
        # assert 0
        # print(f'proto_imgs.shape is {proto_imgs.shape}') # proto_imgs.shape is torch.Size([1600, 3584])
        proto_imgs = proto_imgs[allowed_proto_img_idx]
        proto_img_labels = np.array(proto_img_labels)[allowed_proto_img_idx]

    if config.space == 'feature':
        points_for_protos = discriminator.extract_features(proto_imgs)
        points = discriminator.extract_features(point_imgs)
    elif config.space == 'image':
        points_for_protos = proto_imgs
        points = point_imgs
    else:
        raise NotImplementedError(f"Unknown RW space: {config.space}")

    protos = compute_class_centroids(points_for_protos, proto_img_labels, config.n_examples_per_proto)
    point_to_proto_probs, proto_to_point_probs, point_to_point_probs = compute_transition_probs(
        points, protos, config.similarity_measure, config.dot_product_scale)

    walker_loss = compute_walker_loss(
        config, point_to_proto_probs, proto_to_point_probs,
        point_to_point_probs, target_dist=target_dist, step_weights=step_weights)
    visit_loss = compute_visit_loss(proto_to_point_probs)

    return walker_loss, visit_loss


def compute_transition_probs(points: Tensor, protos: Tensor, similarity_measure: str, dot_product_scale: float=3.0) -> Tensor:
    """
    Computes transition probabilities: point -> proto, proto -> point and point -> point
    """
    assert points.shape[1] == protos.shape[1]
    n_points, n_protos, hid_dim = points.shape[0], protos.shape[0], points.shape[1]

    if similarity_measure == 'l2_distance':
        points_to_protos_sims = -compute_pairwise_l2_dists(points, protos)
        points_to_points_sims = -compute_pairwise_l2_dists(points, points)
    elif similarity_measure == 'dot_product':
        points = (points / points.norm(dim=1, keepdim=True)) * dot_product_scale
        protos = (protos / protos.norm(dim=1, keepdim=True)) * dot_product_scale
        points_to_protos_sims = points @ protos.t() # [n_points, n_protos]
        points_to_points_sims = points @ points.t() # [n_points, n_points]
    else:
        raise NotImplementedError(f'Unknown similarity measure: {similarity_measure}')

    # Suppress diagonal elements
    points_to_points_sims -= (torch.eye(n_points, device=points.device) * 1000)
    # diag_idx = np.diag_indices(n_points)
    # points_to_points_sims[diag_idx[0], diag_idx[1]] = -1000

    assert points_to_protos_sims.shape == (n_points, n_protos), f"Wrong shape: {points_to_protos_sims.shape}"
    assert points_to_points_sims.shape == (n_points, n_points), f"Wrong shape: {points_to_points_sim.shape}"

    point_to_proto_probs = points_to_protos_sims.softmax(dim=1) # [n_points, n_protos]
    proto_to_point_probs = points_to_protos_sims.t().softmax(dim=1) # [n_protos, n_points]
    point_to_point_probs = points_to_points_sims.softmax(dim=1) # [n_points, n_points]

    assert point_to_proto_probs.shape == (n_points, n_protos), f"Wrong shape: {point_to_proto_probs.shape}"
    assert proto_to_point_probs.shape == (n_protos, n_points), f"Wrong shape: {proto_to_point_probs.shape}"
    assert point_to_point_probs.shape == (n_points, n_points), f"Wrong shape: {point_to_point_probs.shape}"

    return point_to_proto_probs, proto_to_point_probs, point_to_point_probs


def compute_walker_loss(
    config: Config, point_to_proto_probs: Tensor, proto_to_point_probs: Tensor,
    point_to_point_probs: Tensor, target_dist: str, step_weights: Tensor=None) -> Tensor:
    """
    Computes walker loss for either diagonal or uniform target distribution

    @param target_dist [str]:
    """
    assert target_dist in ['diag', 'uniform'], f"Unknown target dist: {target_dist}"

    total_loss = 0
    class_visit_loss_coef = config.get('class_visit_loss_coef', 0.0)
    n_points, n_protos = point_to_proto_probs.shape
    curr_p2p_probs = torch.eye(n_points, device=point_to_point_probs.device)
    class_visit_loss = 0.0
    step_weights = step_weights if not step_weights is None else generate_step_weights(config)
    step_weights = step_weights.to(point_to_proto_probs.device)

    for step, curr_alpha in zip(range(config.num_steps + 1), step_weights):
        if class_visit_loss_coef > 0:
            class_visit_loss += class_visit_loss_coef * compute_point_to_point_class_visit_loss(
                curr_p2p_probs, config.n_examples_per_proto)

        curr_transition = (proto_to_point_probs @ curr_p2p_probs) @ point_to_proto_probs
        curr_transition = torch.clamp(curr_transition, 1e-10, 1 - 1e-10)

        probs = curr_transition.diag() if target_dist == 'diag' else curr_transition.flatten()

        if config.loss_type == 'cross_entropy':
            loss = -probs.log().mean()
        elif config.loss_type == 'entropy':
            loss = -(probs * probs.log()).mean()
        else:
            raise NotImplementedError(f'Unknown loss type: {config.loss_type}')

        assert loss >= 0, f"Cross-Entropy or Entropy cannot be negative (step {step}): {loss}: {curr_transition}"

        total_loss += curr_alpha * loss
        curr_p2p_probs = curr_p2p_probs @ point_to_point_probs

    return total_loss


def compute_visit_loss(protos_to_point_probs: Tensor) -> Tensor:
    proto_start_probs = protos_to_point_probs.mean(dim=0)
    proto_start_probs = torch.clamp(proto_start_probs, 1e-10, 1 - 1e-10)
    ce_with_uniform_dist = -proto_start_probs.log().mean()

    return ce_with_uniform_dist


def compute_class_centroids(feats: Tensor, labels: List[int], n_examples_per_proto: int) -> Tensor:
    """
    For each class, computes the class centroid (i.e. mean feature) for this class
    returns: a matrix of shape [num_classes, hid_dim]
    """
    assert feats.ndim == 2, "We should work in features space instead of image space"
    assert len(feats) == len(labels)

    unique_labels = np.unique(labels)
    hid_dim = feats.shape[1]

    # labels_idx = [np.where(labels == y)[0] for y in unique_labels] # Slower, but more concise
    # centroids = torch.stack([feats[idx].mean(dim=0) for idx in labels_idx])
    centroids = feats.view(len(unique_labels), n_examples_per_proto, hid_dim).mean(dim=1)

    assert centroids.shape == (len(unique_labels), feats.size(1)), f"Wrong shape: {centroids.shape}"

    return centroids


def compute_pairwise_l2_dists(xs: Tensor, ys: Tensor) -> Tensor:
    """
    Computes pairwise L2 distances between two sets of vectors
    @param xs: vectors of size [num_xs, feat_dim]
    @param ys: vectors of size [num_ys, feat_dim]
    """
    assert xs.shape[1] == ys.shape[1], f"xs and ys should have the same feat dim, got {xs.shape} and {ys.shape}"
    num_xs, num_ys, feat_dim = xs.shape[0], ys.shape[0], xs.shape[1]

    xx = (xs * xs).sum(dim=1) # [num_xs]
    yy = (ys * ys).sum(dim=1) # [num_ys]
    xy = (xs @ ys.t()) # [num_xs, num_ys]
    l2_dists = xx.view(num_xs, 1) + yy.view(1, num_ys) - 2 * xy

    return l2_dists


def compute_point_to_point_class_visit_loss(point_to_point_probs: Tensor, n_examples_per_class: int) -> Tensor:
    """
    Computes class visit loss for point-to-point transition matrix.

    @param point_to_point_probs: point to point probs transition matrix; of size [n_points, n_points]
    """
    n_points = point_to_point_probs.shape[0]
    assert n_points % n_examples_per_class == 0, f"num_points: {n_points} and n_examples_per_class: {n_examples_per_class}"
    n_classes = n_points // n_examples_per_class
    class_probs = point_to_point_probs.view(n_points, n_classes, n_examples_per_class).sum(dim=2)
    class_logits = (torch.clamp(class_probs, 1e-10, 1.0)).log()
    targets = torch.arange(n_classes).view(n_classes,1).repeat(1, n_examples_per_class).view(n_points)
    targets = targets.to(point_to_point_probs.device)
    class_visit_loss = F.cross_entropy(class_logits, targets)

    return class_visit_loss


def compute_rw_imitative_loss(config, data_layer, dataset, netD, netG) -> Tensor:
    """
    Computes imitative random walk loss, i.e. tries to classify well Generator's samples
    """
    blobs = data_layer.forward()
    # Manually genearting labels of the kind [1,1,1,2,2,2,3,3,3,...] to compute prototypes
    labels = torch.arange(dataset.train_cls_num).unsqueeze(1).repeat(1, config.rw_params.n_examples_per_proto).view(-1)
    # labels = torch.arange(dataset.train_cls_num).unsqueeze(1).repeat(1, 1).view(-1)
    text_feat = np.array([dataset.train_text_feature[i, :] for i in labels])
    text_feat = torch.from_numpy(text_feat.astype('float32')).cuda()

    # z = torch.randn(len(labels), config.z_dim).cuda()
    # G_sample = netG(z, text_feat)
    # z = torch.randn(len(labels), config.z_dim).cuda()
    z = torch.zeros(len(labels), config.z_dim).cuda()
    G_sample = netG(z, text_feat)

    step_weights = netG.get_alpha() if config.rw_params.learnable_alpha else generate_step_weights(config.rw_params)
    rw_walker_loss, rw_visit_loss = compute_random_walk_loss(
        config.rw_params, netD, G_sample, labels, G_sample, 'diag', labels, step_weights=step_weights)

    assert np.isfinite(rw_walker_loss.detach().cpu().numpy()), f"bad rw_walker_loss: {rw_walker_loss}"
    assert np.isfinite(rw_visit_loss.detach().cpu().numpy()), f"bad rw_visit_loss: {rw_visit_loss}"

    return rw_walker_loss, rw_visit_loss


def compute_rw_real_loss(config, data_layer, dataset, netD, netG) -> Tensor:
    """
    Computes real random walk loss, i.e. tries to classify real samples
    """
    blobs = data_layer.forward()
    X = torch.from_numpy(blobs['data']).cuda()
    y = blobs['labels'].astype(int)  # class labels
    # Manually genearting labels of the kind [1,1,1,2,2,2,3,3,3,...] to compute prototypes
    labels = torch.arange(dataset.train_cls_num).unsqueeze(1).repeat(1, config.rw_params.n_examples_per_proto).view(-1)
    text_feat = np.array([dataset.train_text_feature[i, :] for i in labels])
    text_feat = torch.from_numpy(text_feat.astype('float32')).cuda()
    # z = torch.randn(len(labels), config.z_dim).cuda()
    z = torch.zeros(len(labels), config.z_dim).cuda()
    G_sample = netG(z, text_feat)
    step_weights = netG.get_alpha() if config.rw_params.learnable_alpha else generate_step_weights(config.rw_params)
    rw_params = config.rw_params.overwrite(Config({'class_visit_loss_coef': 0})) # Disable class visit loss for RW_real
    rw_walker_loss, rw_visit_loss = compute_random_walk_loss(
        rw_params, netD, G_sample, labels, X, 'diag', y, step_weights=step_weights)

    assert np.isfinite(rw_walker_loss.detach().cpu().numpy()), f"bad rw_walker_loss: {rw_walker_loss}"
    assert np.isfinite(rw_visit_loss.detach().cpu().numpy()), f"bad rw_visit_loss: {rw_visit_loss}"

    return rw_walker_loss, rw_visit_loss


def compute_rw_creative_loss(config, data_layer, dataset, netD, G_creative_sample, netG) -> Tensor:
    """
    Computes creative random walk loss, i.e. tries to classify badly creative Generator's samples
    """
    blobs = data_layer.forward()
    # Manually genearting labels of the kind [1,1,1,2,2,2,3,3,3,...] to compute prototypes
    labels = torch.arange(dataset.train_cls_num).unsqueeze(1).repeat(1, config.rw_params.n_examples_per_proto).view(-1)
    text_feat = np.array([dataset.train_text_feature[i, :] for i in labels])
    text_feat = torch.from_numpy(text_feat.astype('float32')).cuda()
    # z = torch.randn(len(labels), config.z_dim).cuda()
    z = torch.zeros(len(labels), config.z_dim).cuda()
    G_sample = netG(z, text_feat)
    step_weights = netG.get_alpha() if config.rw_params.learnable_alpha else generate_step_weights(config.rw_params)
    rw_params = config.rw_params.overwrite(Config({'class_visit_loss_coef': 0})) # Disable class visit loss for RW_creative

    rw_creative_walker_loss, rw_creative_visit_loss = compute_random_walk_loss(
        rw_params, netD, G_sample, labels, G_creative_sample, 'uniform', step_weights=step_weights)

    assert np.isfinite(rw_creative_walker_loss.detach().cpu().numpy()), f"bad rw_creative_walker_loss: {rw_creative_walker_loss}"
    assert np.isfinite(rw_creative_visit_loss.detach().cpu().numpy()), f"bad rw_creative_visit_loss: {rw_creative_visit_loss}"

    return rw_creative_walker_loss, rw_creative_visit_loss


def generate_step_weights(config: Config):
    assert not config.learnable_alpha

    return torch.tensor([config.decay_coef ** n for n in range(config.num_steps + 1)])