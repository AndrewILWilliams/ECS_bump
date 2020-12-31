# <div align="center"> ECS_Bump </div>
Repo to reproduce the results of Meraner et al. (2013) and Seeley and Jeevanjee (2020) with RRTMG and PyRADS


Created/Mantained By: Andrew Williams (andrew.williams@physics.ox.ac.uk)
Other Contributors: ()

<p align="center">
  <img src="Example_rrtmg_fig.png" width="900" />
</p>

> Abstract: 

### To-do

 - [x] Go through a couple of the `climlab` tutorials and get a simple SCM model going. 
 - [x] Iterate through various surface temperatures and calculate the ECS for each one.
 - [ ] Calculate decomposition into $F_2x$ and $lambda_eff$ terms.
 
 - [ ] Qu: Can RRTMG give the spectrally resolved OLR? Like, averaged in its 14 LW bands? That would be cool
 
 - [ ] Use RRTMG for a simple spectral decomposition of the OLR changes. Do we see the `H20 windows` and `C02 radiator fins`??

### Installation

An `environment.txt` file is provided from which you can generate an `rce_bump` environment with the command `conda create --name rce_bump --file environment.txt`. 

To add this environment to you `jupyter lab` instance, you must first activate this environment and then run `ipython kernel install --user --name=rce_bump`.


### Acknowledgements:

Thanks to Brian Rose for creating `climlab`, which allows for a convenient Python interface to RRTMG, and also a suite of exciting options for open-source climate modelling!

### References:

1) Seeley, J. T., & Jeevanjee, N. (2020). H2O windows and CO2 radiator fins: a clear‐sky explanation for the peak in ECS. Geophysical Research Letters, 47, e2020GL089609. https://doi.org/10.1029/2020GL089609

2) Meraner, K., Mauritsen, T., and Voigt, A. (2013), Robust increase in equilibrium climate sensitivity under global warming, Geophys. Res. Lett., 40, 5944– 5948, doi:10.1002/2013GL058118.
