#!/usr/bin/env python3
import batman
import numpy as np
import matplotlib.pyplot as plt
import os

object_name = input("目標天体名を入力してください: ")
os.chdir(object_name)
params = batman.TransitParams()
params.t0 = 0.                       #time of inferior conjunction
params.per = 1.58                      #orbital period
params.rp = x                      #planet radius (in units of stellar radii)
params.a = 3.136                      #semi-major axis (in units of stellar radii)
params.inc = 88.7                      #orbital inclination (in degrees)
params.ecc = 0.                      #eccentricity
params.w = 90.                       #longitude of periastron (in degrees)
params.u = [0.048, 0.350]                #limb darkening coefficients [u1, u2]
params.limb_dark = "quadratic"       #limb darkening model

t = np.linspace(-0.25, 0.3, 174)

m = batman.TransitModel(params, t)    #initializes model
flux = m.light_curve(params)          #calculates light curve

