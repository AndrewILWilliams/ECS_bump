#!/bin/bash 
#SBATCH --partition=short-serial 
#SBATCH --job-name=pyrads_run
#SBATCH -o ./log/%j.out 
#SBATCH -e ./log/%j.err
#SBATCH --time=24:00:00

conda activate ecsbump

python /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump/run_pyrads.py --temp=281
