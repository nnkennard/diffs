#!/bin/bash
#SBATCH --job-name=ngramArray
#SBATCH --nodes=1 --ntasks=1
#SBATCH --output=logs/test_%A_%a.out
#SBATCH --error=logs/test_%A_%a.err
#SBATCH --array=0-36

array=( $(seq 2018 2023 ) )

python get_ngrams.py -d ../data -c iclr_${array[$SLURM_ARRAY_TASK_ID]}
