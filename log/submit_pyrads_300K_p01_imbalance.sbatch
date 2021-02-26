#!/bin/bash 
#SBATCH --partition=short-serial 
#SBATCH --job-name=300K_run 
#SBATCH -o ./log/run_300K.out 
#SBATCH -e ./log/run_300K.err 
#SBATCH --time=24:00:00

conda activate ecsbump

python /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump/run_pyrads_imbalance.py --temp=300 --imbalance=0.01
