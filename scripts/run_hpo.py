#!/usr/bin/env python

import os
import random
import argparse
from typing import Dict, List, Any, Callable

from firelab.config import Config
from firelab.hpo import compute_hpo_vals_idx

random.seed(42)


def generate_experiments_from_hpo_grid(hpo_grid):
    experiments_vals_idx = compute_hpo_vals_idx(hpo_grid)
    experiments_vals = [{p: hpo_grid[p][i] for p, i in zip(hpo_grid.keys(), idx)} for idx in experiments_vals_idx]

    return experiments_vals


def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Running LLL trainer')
    parser.add_argument('-n', '--num_runs', default=1, type=int, help='Number of runs for each experimental setup')
    parser.add_argument('-d', '--dataset', type=str, help='Which dataset to run on?')
    parser.add_argument('-s', '--split', type=str, help='easy/hard split')
    parser.add_argument('-e', '--experiment', type=str, help='Which HPO experiment to run.')
    parser.add_argument('--is_val', action='store_true', help='Should we run on a validation set?')
    parser.add_argument('--is_gbu', action='store_true', help='Are we running on a GBU dataset?')
    parser.add_argument('--count', action='store_true', help='Flag which says that we just need to count the experiments.')
    parser.add_argument('--print', action='store_true', help='Flag which says that we just need to print the CLI arguments.')
    parser.add_argument('--setting', default='basic', type=str, help='which setting to run? basic | sc (stable '
                                                                     'center) | ld (lower transition matrix) | all | '
                                                                     'np (number of prototypes per class)')

    return parser.parse_args()


def main():
    args = read_args()
    hpos = Config.load('scripts/hpos_reduced.yml')[args.experiment]

    experiments_vals = generate_experiments_from_hpo_grid(hpos.grid)
    if hpos.search_type == 'random':
        experiments_vals = random.sample(experiments_vals, min(hpos.num_experiments, len(experiments_vals)))

    experiments_vals.extend([b.to_dict() for b in hpos.get('baselines', [])])
    experiments_vals = [{p.replace('|', '.'): v for p, v in exp.items()} for exp in experiments_vals]
    experiments_cli_args = [' '.join([f'--rw_config.{p} {v}' for p, v in exp.items()]) for exp in experiments_vals]

    if args.count:
        print(f'Total number of experiments: {len(experiments_cli_args)} x [{args.num_runs} seed] = {len(experiments_cli_args) * args.num_runs}')
    elif args.print:
        run_hpo(args, experiments_cli_args, print_only=True)
    else:
        run_hpo(args, experiments_cli_args)


def run_hpo(args, experiments_cli_args, print_only: bool=False):
    logs_dir = f'/ibex/scratch/yik/rwzsl/batch_logs/{args.setting}/{args.experiment}/{args.dataset}-{args.split}'
    val_flag = "--is_val" if args.is_val else ""
    if args.setting == 'basic':
        trainer = 'train_GBU.py' if args.is_gbu else 'train.py'
    elif args.setting == 'sc':
        trainer = 'train_GBU_stable_c.py' if args.is_gbu else 'train_stable_c.py'
    elif args.setting == 'ld':
        trainer = 'train_GBU_ld.py' if args.is_gbu else 'train_ld.py'
    # elif args.setting == 'np': # included
    #     trainer = 'train_GBU_np.py' if args.is_gbu else 'train_np.py'
    elif args.setting == 'all':  # clean version
        trainer = 'train_GBU_all.py' if args.is_gbu else 'train_all.py'

    if not print_only:
        os.makedirs(logs_dir, exist_ok=True)

    for random_seed in range(1, args.num_runs + 1):
        common_cli_args = f'--dataset {args.dataset} --splitmode {args.split} --manualSeed {random_seed} {val_flag}'

        for cli_args in experiments_cli_args:
            command = f'sbatch -o {logs_dir}/output-%j.log --export=ALL,cli_args="{common_cli_args} {cli_args},trainer={trainer}" scripts/run_slurm_job.sh'

            if print_only:
                print(command)
            else:
                os.system(command)


if __name__ == "__main__":
    main()