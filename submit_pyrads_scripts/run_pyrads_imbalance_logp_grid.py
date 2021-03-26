import xarray as xr
import numpy as np
import climlab

import scipy.integrate as sp  #Gives access to the ODE integration package

import pyrads


import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--temp',
    type=int,
    nargs='+',
    help='Target temperature for CO2 optimization',
    required=True
)

parser.add_argument(
    '--imbalance',
    type=float,
    nargs='+',
    help='Target imbalance',
    required=True
)

args = parser.parse_args()

temp             = args.temp[0]
target_imbalance = args.imbalance[0]

print(temp, target_imbalance)

""" Functions """
# Define functions
def pseudoadiabat(T,p):
    return climlab.utils.thermo.pseudoadiabat(T, p)

def dry_adiabat(T):
    return np.divide(params.params.R_a, cp_a)

def generate_idealized_temp_profile(SST, Tstrat, plevs):
    solution = sp.odeint(pseudoadiabat, SST, np.flip(plevs))
    temp = solution.reshape(-1)
    temp[np.where(temp<Tstrat)] = Tstrat
    return np.flip(temp) # need to re-invert the pressure axis


""" PyRADS setup """
def calc_olr_pyrads(SST, CO2ppmv, Tstrat=200, dnu=0.01, nu_min=0.1, nu_max=3500, npres=1000):
    from scipy.integrate import trapz,simps,cumtrapz

    class Dummy:
        pass

    params_pyrads = Dummy()

    params_pyrads.Rv = pyrads.phys.H2O.R # moist component
    params_pyrads.cpv = pyrads.phys.H2O.cp
    params_pyrads.Lvap = pyrads.phys.H2O.L_vaporization_TriplePoint
    params_pyrads.satvap_T0 = pyrads.phys.H2O.TriplePointT
    params_pyrads.satvap_e0 = pyrads.phys.H2O.TriplePointP
    params_pyrads.esat = lambda T: pyrads.Thermodynamics.get_satvps(T,
                                                                    params_pyrads.satvap_T0,
                                                                    params_pyrads.satvap_e0,
                                                                    params_pyrads.Rv,
                                                                    params_pyrads.Lvap)

    params_pyrads.R = pyrads.phys.air.R  # dry component
    params_pyrads.R_CO2 = pyrads.phys.CO2.R
    params_pyrads.cp = pyrads.phys.air.cp
    params_pyrads.ps_dry = 1e5           # surface pressure of dry component

    params_pyrads.g = 9.81             # surface gravity
    params_pyrads.cosThetaBar = 3./5.  # average zenith angle used in 2stream eqns
    params_pyrads.RH = 0.8             # relative humidity

    # setup resolution
    N_press = npres
    dwavenr = dnu

    wavenr_min = nu_min  # [cm^-1]
    wavenr_max = nu_max  #

    # setup grid:
    g = pyrads.SetupGrids.make_grid(SST,Tstrat,N_press,
                                    wavenr_min,wavenr_max,dwavenr,
                                    params_pyrads,RH=params_pyrads.RH )

    # Set stratospheric spec hum to tropopause value (approximate)
    if np.any(g.T==Tstrat):
        mask = g.T<=Tstrat
        q_trop = g.q[~mask][0]
        g.q[mask] = q_trop
    
    # compute optical thickness:
    g.tau, g.tau_h2o, g.tau_co2 = pyrads.OpticalThickness.compute_tau_H2ON2_CO2dilute(g.p, g.T, g.q, 
                                                                                      CO2ppmv/1e6, g, 
                                                                                      params_pyrads, RH=params_pyrads.RH)
    
    # compute Planck functions etc:
    T_2D = np.transpose(np.tile( g.T, (g.Nn,1) )) # shape=(g.p,g.n)
    g.B_surf = np.pi* pyrads.Planck.Planck_n( g.n, SST ) # shape=(g.n)
    g.B = np.pi* pyrads.Planck.Planck_n( g.wave, T_2D ) # shape=(g.p,g.n)
    # compute OLR etc:
    olr_spec = pyrads.Get_Fluxes.Fplus_alternative(0,g) # (spectrally resolved=irradiance)
    olr = simps(olr_spec,g.n)
    
    return olr, olr_spec #, g


""" Main loop """
# Baseline OLR value to optimize against
OLR0 = calc_olr_pyrads(SST=288,CO2ppmv=280)[0]

CO2_init = 300

olr = calc_olr_pyrads(SST=temp,CO2ppmv=CO2_init)[0]

imbalance = (olr-OLR0)*1

j=0
co2_trial = CO2_init
while np.abs(imbalance)>target_imbalance:

    if j==0:
        print('Initial: ', 'SST=',int(temp), ', CO2=',co2_trial, ', TOA imbalance=',imbalance,' W/m2')
        j=1
    
    F2x = 5 # W/m2
    co2_trial = co2_trial * np.power(2, (olr-OLR0)/F2x)

    olr, olr_spec = calc_olr_pyrads(SST=temp,CO2ppmv=co2_trial)
    
    imbalance = (olr-OLR0)*1
    
    print(f"CO2_init={CO2_init}, currently={co2_trial}. Initial={imbalance} W/m2.")

print('Final:   ', 'SST=',int(temp), ', CO2=',co2_trial, ', TOA imbalance=',imbalance,' W/m2')
CO2_outp = np.array([co2_trial])

np.save(f"../Data/PyRADS/co2_{temp}K_1000_logplevs_p01dnu", CO2_outp)

print("Calculating lambda...")
olrp1, olr_specp1 = calc_olr_pyrads(SST=temp+1,CO2ppmv=co2_trial)

lambda_spec = (olr_specp1-olr_spec)*1
np.save(f"../Data/PyRADS/lambdanu_{temp}K_1000_logplevs_p01dnu", lambda_spec)