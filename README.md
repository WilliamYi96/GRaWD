# GRaWD
The official implementation of Generative Random Walk Deviation Loss for Improved Unseen Learning Representation. CVPR 2021 under review.

# Requirements
## Packages
Python 3.6, Pytorch 1.6, sklearn, scipy, matplotlib, random, copy and other general packages

## Processed Feature Data 
You can download the text-based dataset at [dataset CUBird and NABird](https://www.dropbox.com/s/9qovr86kgogkl6r/CUB_NAB_Data.zip). For attribute-based data, you can access to [here](https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/zero-shot-learning/zero-shot-learning-the-good-the-bad-and-the-ugly). 

Please put the uncompressed data to the folder "data".

## Training and Testing
We provide integrated code for training and testing. 

### Training on text-based datasets
```
cd 'your main folder'

python train.py --dataset CUB --splitmode easy --exp_name 'CUB_easy_Rep' --rw_config_path ./configs/CUB_easy_Best_HPs.yml
python train.py --dataset CUB --splitmode hard --exp_name 'CUB_hard_Rep' --rw_config_path ./configs/CUB_hard_Best_HPs.yml
python train.py --dataset NAB --splitmode easy --exp_name 'NAB_easy_Rep' --rw_config_path ./configs/NAB_easy_Best_HPs.yml
python train.py --dataset NAB --splitmode hard --exp_name 'NAB_hard_Rep' --rw_config_path ./configs/NAB_hard_Best_HPs.yml
```

### Training on attribute-based datasets
```
cd 'your main folder'

python train.py --dataset CUB --splitmode easy --exp_name 'CUB_easy_Rep' --rw_config_path ./configs/CUB_easy_Best_HPs.yml
python train.py --dataset CUB --splitmode hard --exp_name 'CUB_hard_Rep' --rw_config_path ./configs/CUB_hard_Best_HPs.yml
python train.py --dataset NAB --splitmode easy --exp_name 'NAB_easy_Rep' --rw_config_path ./configs/NAB_easy_Best_HPs.yml
python train.py --dataset NAB --splitmode hard --exp_name 'NAB_hard_Rep' --rw_config_path ./configs/NAB_hard_Best_HPs.yml
```


Here we provide the potential best hyper-parameters that can reproduce our reported results. You can refer to the logs under main folder for the training details. For each trial, the final performance may vary a little bit. Following standard setting, we report the best performance after k-trials. 

## Reference
- Yizhe Zhu, Mohamed Elhoseiny, Bingchen Liu, Xi Peng and Ahmed Elgammal "A Generative Adversarial Approach for Zero-Shot Learning from Noisy Texts", CVPR, 2018          
- Mohamed Elhoseiny, Mohamed Elfeki, Creativity Inspired Zero Shot Learning, Thirty-sixth International Conference on Computer Vision (ICCV), 2019              
- Elhoseiny, Mohamed, Kai Yi, and Mohamed Elfeki. "CIZSL++: Creativity Inspired Generative Zero-Shot Learning." arXiv preprint arXiv:2101.00173 (2021).  

If you find this code is useful, please cite:

```
@article{grawd,
  title={Generative Random Walk Deviation Loss for Improved Unseen Learning Representation},
  author={Divyansh, Jha and Kai, Yi and Ivan Skorokhodov, Ivan and Elhoseiny, Mohamed},
  journal={CVPR 2021 under review},
  year={2021}
}
