"""
Domain Generalization (Generalized) Zero-Shot Learning Batch Running Script
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
    parser.add_argument('--trainer', type=str, default='/ibex/scratch/yik/MLCE/DZSL/dzsl.py')
    parser.add_argument('--root_dir', type=str, default='/ibex/scratch/yik/GZSL-Survey/methods/gzsl/GAZSL')
    parser.add_argument('--gzsl', action='store_true', help='DZSL experiment or DGZSL experiment?')
    parser.add_argument('--text_dataset', '-td', action='store_true')
    return parser.parse_args()


def main(args):
    # Ablations on extrapolations and interpolations
    trainer = f'{args.roo_dir}/train_extp_abs.py'
    EXTP = [0, 1, 2, 3, 4]
    SPLITMODES = ['easy', 'hard']
    for r in range(1, args.num_runs + 1):
        for splitmode in SPLITMODES:
            for extp in EXTP:
                job_name = f'grawd_abs_cub_{splitmode}_extp{extp}_r{r}'
                out_name = f'grawd_abs_cub_{splitmode}_extp{extp}_r{r}.out'
                err_name = f'grawd_abs_cub_{splitmode}_extp{extp}_r{r}.err'

                slurm_script = f'{args.root_dir}/scripts/slurm.sh'
                cli_args = f' --dataset {dataset} --preprocessing --z_dim {z_dim} --runs {r}'

                command = f'sbatch -J {job_name} -o {out_name} -e {err_name} ' \
                          f'--export=ALL,cli_args="{trainer} {cli_args}" {slurm_script}'
                os.system(command)


    # Training and evaluating attribute-based datasets
    if not args.text_dataset:
        DATASETS = ['APY', 'AWA1', 'AWA1', 'SUN', 'CUB']
        for r in range(1, args.num_runs+1):
            for dataset in DATASETS:
                trainer = f'{args.root_dir}/train_GBU.py'
                job_name = f'gazsl_att_{dataset}_{r}'
                out_name = f'gazsl_att_{dataset}_{r}.out'
                err_name = f'gazsl_att_{dataset}_{r}.err'

                if dataset == 'CUB':
                    z_dim = 100
                else:
                    z_dim = 10

                slurm_script = f'{args.root_dir}/scripts/slurm.sh'
                cli_args = f' --dataset {dataset} --preprocessing --z_dim {z_dim} --runs {r}'

                command = f'sbatch -J {job_name} -o {out_name} -e {err_name} ' \
                          f'--export=ALL,cli_args="{trainer} {cli_args}" {slurm_script}'
                os.system(command)

    else:
        # Training and evaluating text-based datasets
        SPLITMODE = ['easy', 'hard']
        DATASETS = ['CUB', 'NAB']
        for r in range(1, args.num_runs+1):
            for splitmode in SPLITMODE:
                for dataset in DATASETS:
                    trainer = f'{args.root_dir}/train_{dataset}.py'
                    job_name = f'gazsl_text_{dataset}_{splitmode}_{r}'
                    out_name = f'gazsl_text_{dataset}_{splitmode}_{r}.out'
                    err_name = f'gazsl_text_{dataset}_{splitmode}_{r}.err'

                    slurm_script = f'{args.root_dir}/scripts/slurm.sh'
                    cli_args = f' --dataset {dataset} --splitmode {splitmode} --runs {r}'

                    command = f'sbatch -J {job_name} -o {out_name} -e {err_name} ' \
                              f'--export=ALL,cli_args="{trainer} {cli_args}" {slurm_script}'
                    os.system(command)


if __name__ == "__main__":
    args = read_args()
    main(args=args)
