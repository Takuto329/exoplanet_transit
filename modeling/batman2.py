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
params.rp = 0.118104034                      #planet radius (in units of stellar radii)
params.a = 3.136                      #semi-major axis (in units of stellar radii)
params.inc = 88.7                      #orbital inclination (in degrees)
params.ecc = 0.                      #eccentricity
params.w = 90.                       #longitude of periastron (in degrees)
params.u = [0.048, 0.350]                #limb darkening coefficients [u1, u2]
params.limb_dark = "quadratic"       #limb darkening model

t = np.linspace(-0.25, 0.3, 174)

m = batman.TransitModel(params, t)    #initializes model
flux = m.light_curve(params)          #calculates light curve

with open('GJ1214,k2.txt', 'r') as file:
    lines = file.readlines()

# 各行の数値を取得
data = [float(line.strip()) for line in lines]

x = np.linspace(-0.25, 0.3, 174)  # -5から5の範囲で100個の点を生成

# y=2xの関数を計算
y = np.full_like(x, 1- (0.11833 ** 2))
z = np.full_like(x, 1- (0.126081631 ** 2))
# グラフを描画
plt.plot(x, y,color = "black")
plt.plot(x, z,color = "red")
plt.plot(t, flux)
plt.scatter(t, data, marker=".", color = "black")

plt.ylim(0.97,1.03)
plt.xlabel("Time from central transit")
plt.ylabel("Relative flux")
plt.legend()
plt.show()
plt.savefig("img.png",transparent=True,dpi=300)