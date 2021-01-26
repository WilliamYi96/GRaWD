# GRaWD
The official implementation of Generative Random Walk Deviation Loss for Improved Unseen Learning Representation. CVPR 2021 under review.

# Requirements
Python 3.6, Pytorch 1.6, sklearn, scipy, matplotlib, random, copy and other general packages

# Processed Feature Data 
You can download the text-based dataset at [dataset CUBird and NABird](https://www.dropbox.com/s/9qovr86kgogkl6r/CUB_NAB_Data.zip). For attribute-based data, you can access to [here](https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/zero-shot-learning/zero-shot-learning-the-good-the-bad-and-the-ugly). 

Please put the uncompressed data to the folder "data".

# Reproduce CIZSLv2 Best Model
```
python train_cizslv2.py --dataset 'CUB' --splitmode 'easy' --creativity_weight 1  --exp_name 'cizslv2'              
python train_cizslv2.py --dataset 'CUB' --splitmode 'hard' --creativity_weight 0.1  --exp_name 'cizslv2'                
python train_cizslv2.py --dataset 'NAB' --splitmode 'easy' --creativity_weight 0.001  --exp_name 'cizslv2'              
python train_cizslv2.py --dataset 'NAB' --splitmode 'hard' --creativity_weight 1  --exp_name 'cizslv2'
```        

## Reference
- Yizhe Zhu, Mohamed Elhoseiny, Bingchen Liu, Xi Peng and Ahmed Elgammal "A Generative Adversarial Approach for Zero-Shot Learning from Noisy Texts", CVPR, 2018          
- Mohamed Elhoseiny, Mohamed Elfeki, Creativity Inspired Zero Shot Learning, Thirty-sixth International Conference on Computer Vision (ICCV), 2019              

If you find this code is useful, please cite:

```
@article{grawd,
  title={Generative Random Walk Deviation Loss for Improved Unseen Learning Representation},
  author={Divyansh, Jha and Kai, Yi and Ivan Skorokhodov, Ivan and Elhoseiny, Mohamed},
  journal={CVPR 2021 under review},
  year={2021}
}
