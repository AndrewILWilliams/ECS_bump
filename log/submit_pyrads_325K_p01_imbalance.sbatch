#!/bin/bash 
#SBATCH --partition=short-serial 
#SBATCH --job-name=325K_run_p01 
#SBATCH -o ./log/run_325K_p01_imbalance.out 
#SBATCH -e ./log/run_325K_p01_imbalance.err 
#SBATCH --time=24:00:00

conda activate ecsbump

python /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump/run_pyrads_imbalance.py --temp=325 --imbalance=0.01
