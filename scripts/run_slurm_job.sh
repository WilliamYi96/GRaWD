#!/bin/bash
#SBATCH -N 1
#SBATCH --partition=batch
#SBATCH --time=12:00:00
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --constraint=[gtx1080ti|rtx2080ti|v100]

# Checking that our GPU is not taken
echo "`gpustat`"
echo "`nvidia-smi`"
# shellcheck disable=SC2154
echo "CLI args: $cli_args"

# shellcheck disable=SC2164
cd /ibex/scratch/yik/rwzsl

# shellcheck disable=SC2154
python $trainer $cli_args