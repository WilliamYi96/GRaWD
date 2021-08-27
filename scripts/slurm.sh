#!/bin/bash
#SBATCH -N 1
#SBATCH --partition=batch
#SBATCH -J Rep_Best_hps_2
#SBATCH -o Rep_Best_hps_2.%J.out
#SBATCH -e Rep_Best_hps_2.%J.err
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --constraint=[gtx1080ti|rtx2080ti|v100]

#run the application:
# shellcheck disable=SC2164
cd /ibex/scratch/yik/rwzsl

# Checking that our GPU is not taken
echo "`gpustat`"
echo "`nvidia-smi`"
echo "CLI args: $cli_args"

#run the application:
cd /ibex/scratch/yik/rwzsl/

python -u $cli_args
