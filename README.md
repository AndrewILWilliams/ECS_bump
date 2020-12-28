# <div align="center"> RCE_Bump </div>
Repo to reproduce the results of Meraner et al. (2013) and Seeley and Jeevanjee (2020) with RRTMG and PyRADS


Created/Mantained By: Andrew Williams (andrew.williams@physics.ox.ac.uk)
Other Contributors: ()

<p align="center">
  <img src="seeley_jeevanjee_2020.png" width="500" />
</p>

> Abstract: 

### To-do

 - [ ] Go through a couple of the `climlab` tutorials and get a simple RCE model going. 
 - [ ] Iterate through various surface temperatures and calculate the ECS for each one.
 
 - [ ] Use RRTMG for a simple spectral decomposition of the OLR changes. Do we see the `H20 windows` and `C02 radiator fins`??

### Installation

An `environment.txt` file is provided from which you can generate an `rce_bump` environment with the command `conda create --name rce_bump --file environment.txt`. 

To add this environment to you `jupyter lab` instance, you must first activate this environment and then run `ipython kernel install --user --name=rce_bump`.


### Acknowledgements:

**References:**

1) 
