#!/bin/bash 
#SBATCH --partition=high-mem 
#SBATCH --job-name=pyrads_run
#SBATCH -o ../log/%j.out 
#SBATCH -e ../log/%j.err
#SBATCH --time=48:00:00
#SBATCH --mem=128000

conda activate ecsbump

python /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump/run_pyrads.py --temp=281
