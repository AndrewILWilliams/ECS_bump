#!/bin/bash 
#SBATCH --partition=short-serial 
#SBATCH --job-name=301K_run_p01 
#SBATCH -o ../log/run_301K_p01_imbalance.out 
#SBATCH -e ../log/run_301K_p01_imbalance.err 
#SBATCH --time=24:00:00

conda activate ecsbump

python /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump/submit_pyrads_scripts/run_pyrads_imbalance-high_vres.py --temp=301 --imbalance=0.01
