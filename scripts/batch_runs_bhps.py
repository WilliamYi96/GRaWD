"""
Imaginative Walk Scripts for ablation study
Created by Kai Yi on May, 23.
Contact email: williamyi96@gmail.com
ALL RIGHT RESERVED.
"""

import os
import random
import argparse


def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Running LLL trainer')
    parser.add_argument('-n', '--num_runs', default=3, type=int, help='Number of runs for each experimental setup')
    parser.add_argument('-d', '--dataset', type=str, help='Which dataset to run on?', default='PACS')
    parser.add_argument('-m', '--method', type=str, help='Which method to run?', default='CuMix')
    parser.add_argument('--trainer', type=str, default='/ibex/scratch/yik/rwzsl/train_extp.py')
    parser.add_argument('--root_dir', type=str, default='/ibex/scratch/yik/rwzsl')
    parser.add_argument('--gzsl', action='store_true', help='DZSL experiment or DGZSL experiment?')
    parser.add_argument('--text_dataset', '-td', action='store_true')
    return parser.parse_args()


def main(args):
    # Ablations on iddferent interpolation and extrapolations
    EXTPS = [0, 1, 2, 3, 4]
    CUB_EASY_BEST_CONFIG = './configs/CUB_easy_Best_HPs.yml'
    CUB_HARD_BEST_CONFIG = './configs/CUB_hard_Best_HPs.yml'
    CONFIGS = {'easy': CUB_EASY_BEST_CONFIG,
               'hard': CUB_HARD_BEST_CONFIG}
    SPLITMODE = ['easy', 'hard']

    trainer = '/ibex/scratch/yik/rwzsl/train_extp.py'
    i = 0
    for r in range(1, args.num_runs+1):
        for extp in EXTPS:
            for splitmode in SPLITMODE:
                job_name = f'grawd_cub_{splitmode}_r{r}_extp{extp}_{i}'
                out_name = f'grawd_cub_{splitmode}_r{r}_extp{extp}_{i}.out'
                err_name = f'grawd_cub_{splitmode}_r{r}_extp{extp}_{i}.err'

                slurm_script = f'{args.root_dir}/scripts/slurm.sh'
                cli_args = f' --dataset CUB --splitmode {splitmode} --exp_name {job_name} --rw_config_path {CONFIGS[splitmode]} --extp {extp}'

                command = f'sbatch -J {job_name} -o {out_name} -e {err_name} ' \
                          f'--export=ALL,cli_args="{trainer} {cli_args}" {slurm_script}'
                os.system(command)
                i += 1

    # Ablations on gamma, exponential decay
    CONFIG_NO = [1, 2, 3, 4]
    trainer = '/ibex/scratch/yik/rwzsl/train_gamma_abs.py'
    for r in range(1, args.num_runs+1):
        for config in CONFIG_NO:
            for splitmode in SPLITMODE:
                job_name = f'grawd_cub_{splitmode}_r{r}_exp_decay{config}_{i}'
                out_name = f'grawd_cub_{splitmode}_r{r}_exp_decay{config}_{i}.out'
                err_name = f'grawd_cub_{splitmode}_r{r}_exp_decay{config}_{i}.err'

                slurm_script = f'{args.root_dir}/scripts/slurm.sh'

                config_path = f'./configs/CUB_{splitmode}_Best_HPs_{config}.yml'

                cli_args = f' --dataset CUB --splitmode {splitmode} --exp_name {job_name} --rw_config_path {config_path}'

                command = f'sbatch -J {job_name} -o {out_name} -e {err_name} ' \
                          f'--export=ALL,cli_args="{trainer} {cli_args}" {slurm_script}'
                os.system(command)
                i += 1


if __name__ == "__main__":
    args = read_args()
    main(args=args)
