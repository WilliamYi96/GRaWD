## TODOs
#python scripts/run_hpo.py -e nab_hard_big_hpo -d CUB -s hard
#python scripts/run_hpo.py -e nab_hard_big_hpo -d CUB -s easy
#python scripts/run_hpo.py -e nab_hard_big_hpo -d NAB -s hard
#python scripts/run_hpo.py -e nab_hard_big_hpo -d NAB -s easy
#
#python scripts/run_hpo.py -e nab_hard_big_hpo -d AWA2 --is_gbu
#python scripts/run_hpo.py -e nab_hard_big_hpo -d APY --is_gbu
#python scripts/run_hpo.py -e nab_hard_big_hpo -d SUN --is_gbu

######################

#python scripts/run_hpo.py -e nab_hard_big_hpo -d CUB -s hard --setting 'sc'
#python scripts/run_hpo.py -e nab_hard_big_hpo -d CUB -s easy --setting 'sc'
#python scripts/run_hpo.py -e nab_hard_big_hpo -d NAB -s hard --setting 'sc'
#python scripts/run_hpo.py -e nab_hard_big_hpo -d NAB -s easy --setting 'sc'

python scripts/run_hpo.py -e nab_hard_big_hpo -d AWA2 --is_gbu --setting 'sc'
python scripts/run_hpo.py -e nab_hard_big_hpo -d APY --is_gbu --setting 'sc'
python scripts/run_hpo.py -e nab_hard_big_hpo -d SUN --is_gbu --setting 'sc'

######################

#python scripts/run_hpo.py -e nab_hard_big_hpo -d CUB -s hard --setting 'ld'
#python scripts/run_hpo.py -e nab_hard_big_hpo -d CUB -s easy --setting 'ld'
#python scripts/run_hpo.py -e nab_hard_big_hpo -d NAB -s hard --setting 'ld'
#python scripts/run_hpo.py -e nab_hard_big_hpo -d NAB -s easy --setting 'ld'

python scripts/run_hpo.py -e nab_hard_big_hpo -d AWA2 --is_gbu --setting 'ld'
python scripts/run_hpo.py -e nab_hard_big_hpo -d APY --is_gbu --setting 'ld'
python scripts/run_hpo.py -e nab_hard_big_hpo -d SUN --is_gbu --setting 'ld'












## Ablations of interpolation and extrapolations
# Negative extrapolations
# Need to run three times from 1 - 3
python train_extp.py --dataset CUB --splitmode easy --exp_name '0001' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 0
python train_extp.py --dataset CUB --splitmode hard --exp_name '0002' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 0
python train_extp.py --dataset CUB --splitmode easy --exp_name '0003' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 0
python train_extp.py --dataset CUB --splitmode hard --exp_name '0004' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 0
python train_extp.py --dataset CUB --splitmode easy --exp_name '0005' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 0
python train_extp.py --dataset CUB --splitmode hard --exp_name '0006' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 0

python train_extp.py --dataset CUB --splitmode easy --exp_name '0011' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 1
python train_extp.py --dataset CUB --splitmode hard --exp_name '0012' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 1
python train_extp.py --dataset CUB --splitmode easy --exp_name '0013' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 1
python train_extp.py --dataset CUB --splitmode hard --exp_name '0014' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 1
python train_extp.py --dataset CUB --splitmode easy --exp_name '0015' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 1
python train_extp.py --dataset CUB --splitmode hard --exp_name '0016' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 1

python train_extp.py --dataset CUB --splitmode easy --exp_name '0021' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 2
python train_extp.py --dataset CUB --splitmode hard --exp_name '0022' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 2
python train_extp.py --dataset CUB --splitmode easy --exp_name '0023' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 2
python train_extp.py --dataset CUB --splitmode hard --exp_name '0024' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 2
python train_extp.py --dataset CUB --splitmode easy --exp_name '0025' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 2
python train_extp.py --dataset CUB --splitmode hard --exp_name '0026' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 2

python train_extp.py --dataset CUB --splitmode easy --exp_name '0031' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 3
python train_extp.py --dataset CUB --splitmode hard --exp_name '0032' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 3
python train_extp.py --dataset CUB --splitmode easy --exp_name '0033' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 3
python train_extp.py --dataset CUB --splitmode hard --exp_name '0034' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 3
python train_extp.py --dataset CUB --splitmode easy --exp_name '0035' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 3
python train_extp.py --dataset CUB --splitmode hard --exp_name '0036' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 3

python train_extp.py --dataset CUB --splitmode easy --exp_name '0041' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 4
python train_extp.py --dataset CUB --splitmode hard --exp_name '0042' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 4
python train_extp.py --dataset CUB --splitmode easy --exp_name '0043' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 4
python train_extp.py --dataset CUB --splitmode hard --exp_name '0044' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 4
python train_extp.py --dataset CUB --splitmode easy --exp_name '0045' --rw_config_path ./configs/CUB_easy_Best_HPs.yml --extp 4
python train_extp.py --dataset CUB --splitmode hard --exp_name '0046' --rw_config_path ./configs/CUB_hard_Best_HPs.yml --extp 4

# Ablations on gamma, 0.7, 0.8, 0.9, and 1.2, exponential decay
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0111' --rw_config_path ./configs/CUB_easy_Best_HPs_1.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0112' --rw_config_path ./configs/CUB_hard_Best_HPs_1.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0113' --rw_config_path ./configs/CUB_easy_Best_HPs_1.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0114' --rw_config_path ./configs/CUB_hard_Best_HPs_1.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0115' --rw_config_path ./configs/CUB_easy_Best_HPs_1.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0116' --rw_config_path ./configs/CUB_hard_Best_HPs_1.yml

python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0121' --rw_config_path ./configs/CUB_easy_Best_HPs_2.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0122' --rw_config_path ./configs/CUB_hard_Best_HPs_2.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0123' --rw_config_path ./configs/CUB_easy_Best_HPs_2.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0124' --rw_config_path ./configs/CUB_hard_Best_HPs_2.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0125' --rw_config_path ./configs/CUB_easy_Best_HPs_2.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0126' --rw_config_path ./configs/CUB_hard_Best_HPs_2.yml

python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0131' --rw_config_path ./configs/CUB_easy_Best_HPs_3.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0132' --rw_config_path ./configs/CUB_hard_Best_HPs_3.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0133' --rw_config_path ./configs/CUB_easy_Best_HPs_3.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0134' --rw_config_path ./configs/CUB_hard_Best_HPs_3.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0135' --rw_config_path ./configs/CUB_easy_Best_HPs_3.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0136' --rw_config_path ./configs/CUB_hard_Best_HPs_3.yml

python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0141' --rw_config_path ./configs/CUB_easy_Best_HPs_4.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0142' --rw_config_path ./configs/CUB_hard_Best_HPs_4.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0143' --rw_config_path ./configs/CUB_easy_Best_HPs_4.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0144' --rw_config_path ./configs/CUB_hard_Best_HPs_4.yml
python train_gamma_abs.py --dataset CUB --splitmode easy --exp_name '0145' --rw_config_path ./configs/CUB_easy_Best_HPs_4.yml
python train_gamma_abs.py --dataset CUB --splitmode hard --exp_name '0146' --rw_config_path ./configs/CUB_hard_Best_HPs_4.yml

# Experiments on GAZSL AWA2, CUB, we directly use the reported results from CIZSL

# The rest thing is the improvements on TF-VAEGAN aPY dataset
