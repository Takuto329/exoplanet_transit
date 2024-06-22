#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

import exoplanet as xo

# The light curve calculation requires an orbit
orbit = xo.orbits.KeplerianOrbit(period=1.58 )

# Compute a limb-darkened light curve using starry
t = np.linspace(-0.1, 0.1, 1000)
u = [0.088, 0.404]

light_curve = (
    xo.LimbDarkLightCurve(u).get_light_curve(orbit=orbit, r=0.1, t=t, texp=0.02).eval()
)
# Note: the `eval` is needed because this is using Theano in
# the background

plt.plot(t, light_curve)
plt.ylabel("relative flux")
plt.xlabel("time [days]")
plt.xlim(t.min(), t.max());
plt.show()
