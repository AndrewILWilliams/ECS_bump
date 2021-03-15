#!/bin/bash

TEMPS=(280 281 282 283 284 285 286 287 288 289 290 291 292 293 294 295 296 297 298 299 
       300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 
       320 321 322 323 324 325)
            
IMBALANCE=0.01

for temp in "${TEMPS[@]}"; do

  if [ ! -f /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump/Data/PyRADS/co2_${temp}K_300_logplevs_CO2_continuum.npy ]; then
  
    cd /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump
    echo $temp, "log"
    
    cp ./submit_pyrads_scripts/submit_pyrads_run.sbatch ./log/submit_pyrads_${temp}K.sbatch
    

    ## Replace lines in the submission scripts appropriately
    sed -i "3 s+.*+#SBATCH --job-name=${temp}K_run +g" ./log/submit_pyrads_${temp}K.sbatch
    sed -i "4 s+.*+#SBATCH -o ../log/run_${temp}K.out +g" ./log/submit_pyrads_${temp}K.sbatch
    sed -i "5 s+.*+#SBATCH -e ../log/run_${temp}K.err +g" ./log/submit_pyrads_${temp}K.sbatch

    sed -i "10 s+.*+python /gws/nopw/j04/aopp/andreww/side_projects/ECS_bump/submit_pyrads_scripts/run_pyrads_imbalance_logp_grid.py --temp=${temp} --imbalance=${IMBALANCE}+g" ./log/submit_pyrads_${temp}K.sbatch

    #echo "got here!"
    cd rundir
    #echo $PWD
    sbatch ./../log/submit_pyrads_${temp}K.sbatch
    
  fi
  
done