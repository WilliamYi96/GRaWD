#!/bin/bash
#SBATCH -N 1
#SBATCH --partition=batch
#SBATCH -J stable_c_text
#SBATCH -o stable_c_text.%J.out
#SBATCH -e stable_c_text.%J.err
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --constraint=[gtx1080ti|rtx2080ti|v100]

#run the application:
# shellcheck disable=SC2164
cd /ibex/scratch/yik/rwzsl

#python train_GBU.py --dataset APY --preprocessing --exp_name 'aPY_A_stable_c_text' --rw_config_path ./configs/aPY_Best_HPs.yml
#python train_GBU.py --dataset AWA2 --preprocessing --exp_name 'AWA2_A_stable_c_text' --rw_config_path ./configs/AWA2_Best_HPs.yml
#python train_GBU.py --dataset SUN --preprocessing --exp_name 'SUN_A_stable_c_text' --rw_config_path ./configs/SUN_Best_HPs.yml

python train_stable_c.py --dataset CUB --splitmode easy --exp_name 'CUB_easy_stable_c_text' --rw_config_path ./configs/CUB_easy_Best_HPs.yml
python train_stable_c.py --dataset CUB --splitmode hard --exp_name 'CUB_hard_stable_c_text' --rw_config_path ./configs/CUB_hard_Best_HPs.yml
python train_stable_c.py --dataset NAB --splitmode easy --exp_name 'NAB_easy_stable_c_text' --rw_config_path ./configs/NAB_easy_Best_HPs.yml
python train_stable_c.py --dataset NAB --splitmode hard --exp_name 'NAB_hard_stable_c_text' --rw_config_path ./configs/NAB_hard_Best_HPs.yml