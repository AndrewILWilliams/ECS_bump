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

args = parser.parse_args()

temp = args.temp[0]

print(temp)

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
def calc_olr_pyrads(SST, CO2ppmv, Tstrat=200, dnu=0.1, nu_min=0.1, nu_max=3500, npres=30):
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

    
    #  Couple water vapor to radiation
    ## climlab setup
    # create surface and atmosperic domains
    state = climlab.column_state(num_lev=N_press, num_lat=1, water_depth=1.)
    plevs = state['Tatm'].domain.axes['lev'].points
    g.p = plevs*100 # Convert hPa->Pa for PyRADS computation
    
    state['Ts'][:] = SST
    state['Tatm'][:] = generate_idealized_temp_profile(SST, Tstrat, g.p/100) # This function requires pressure in hPa !
    g.T = generate_idealized_temp_profile(SST, Tstrat, g.p/100)
    
    #  fixed relative humidity
    h2o = climlab.radiation.water_vapor.FixedRelativeHumidity(state=state,
                                                              relative_humidity=params_pyrads.RH)
    
    g.q = h2o.q
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
    
    return olr, olr_spec, g


""" Main loop """
# Baseline OLR value to optimize against
OLR0 = calc_olr_pyrads(SST=288,CO2ppmv=280)[0]

# What are the approximate CO2 concentrations we expect to correspond to each temp?
# Take from the rrtmg_lw run
CO2_init = xr.open_dataarray("./Data/C_Ts_curve_RRTMG.nc").sel(Ts=temp).values

olr = calc_olr_pyrads(SST=temp,CO2ppmv=CO2_init)[0]

imbalance = np.round(np.abs(olr-OLR0),3)

print(f"Running loop for T={temp}K, with initial CO2 guess={CO2_init}ppmv.")
j=0
while imbalance>0.2:

    if j==0:
        co2_trial = CO2_init
        print('Initial: ', 'SST=',int(temp), ', CO2=',int(co2_trial), ', TOA imbalance=',imbalance,' W/m2')
        amplification = 1
        j=1

    dG = (np.sign(imbalance))
    co2_trial+=dG 

    if co2_trial<0:
        co2_trial=0
        print("CO2 went below 0 ppmv...")

    olr, _, _ = calc_olr_pyrads(SST=temp,CO2ppmv=co2_trial)

    imbalance = np.round(np.abs(olr-OLR0),3)

print('Final:   ', 'SST=',int(temp), ', CO2=',int(co2_trial), ', TOA imbalance=',imbalance,' W/m2')
CO2_outp = np.array([int(co2_trial)])

np.save(f"./Data/PyRADS/co2_{temp}K", CO2_outp)

