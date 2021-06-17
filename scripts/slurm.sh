#!/usr/bin/env bash
#SBATCH -N 1
#SBATCH --partition=batch
#SBATCH --mail-user=imaginative.walks@gmail.com
#SBATCH --mail-type=END
#SBATCH --time=24:00:00
#SBATCH --mem=36G
#SBATCH --gres=gpu:1
#SBATCH --constraint=[v100]


# Checking that our GPU is not taken
echo "`gpustat`"
echo "`nvidia-smi`"
echo "CLI args: $cli_args"

run the application:
cd /ibex/scratch/yik/GZSL-Survey/methods/gzsl/GAZSL

python -u $cli_args
