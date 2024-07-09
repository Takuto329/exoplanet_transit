import numpy as np
from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt

def model(time, a, b):
    return a * time + b

def calculate_slope(value, time, airmass, O_FLUX, C_FLUX):
    flux = (O_FLUX / C_FLUX) * (10 ** (airmass * value))
    params, covariance = curve_fit(model, time, flux)
    return params[0]


# データの読み込み
df = pd.read_csv(f"/Users/takuto/iriki/GJ1214/A_data/sa.txt", sep=' ')

df2 = df[~((df['TIME'] > 2455788.301) & (df['TIME'] < 2455788.352))] #OOTのところだけをとりだす

time = np.array(df2['TIME'])
airmass = np.array(df2['AIRMASS'])
O_FLUX = np.array(df2['O_FLUX'])
C_FLUX = np.array(df2['C_FLUX'])

# フラックスの計算
# 最適な value を見つける
value_range = np.linspace(-1, 1, 100000)  # 探索する value の範囲
slopes = []

for value in value_range:
    slope = calculate_slope(value, time, airmass, O_FLUX, C_FLUX)
    slopes.append(slope)

min_slope_value = value_range[np.argmin(np.abs(slopes))]
print("small value:", min_slope_value)

flux = (O_FLUX / C_FLUX) * 10**(airmass * min_slope_value)
flux2 = (O_FLUX / C_FLUX) #比較のために生のの



# 最小二乗法でパラメータを推定
params, covariance = curve_fit(model, time, flux)
params2, covariance = curve_fit(model, time, flux2)
print("パラメータ:", params)
print("パラメータ:", params2)

# データとフィットラインのプロット
plt.scatter(time, flux, label='Data', alpha=0.5, color='b')
plt.scatter(time, flux2, label='Data', alpha=0.5, color='r')
plt.plot(time, model(time, *params), label='Fitted line', color='y')
plt.xlabel('Time')
plt.ylabel('Flux')
plt.legend()
plt.show()