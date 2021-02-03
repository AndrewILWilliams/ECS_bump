#!/bin/bash 
#SBATCH --partition=short-serial 
#SBATCH --job-name=pyrads_run
#SBATCH -o ./log/%j.out 
#SBATCH -e ./log/%j.err
#SBATCH --time=24:00:00

conda activate ecsbump

echo pwd

python run_pyrads.py --temp=280