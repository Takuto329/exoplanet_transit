import numpy as np
from scipy.optimize import curve_fit
import pandas as pd
import matplotlib.pyplot as plt

def model(time, a, b):
    return a * time + b

def axb(value, time_OOT, airmass_OOT, object_flux_OOT, compa_flux_OOT):
    flux = (object_flux_OOT / compa_flux_OOT) * (10 ** (airmass_OOT * value))
    params, covariance = curve_fit(model, time_OOT, flux)
    return params


# データの読み込み
df = pd.read_csv(f"/Users/takuto/iriki/GJ1214/A_data/sa.txt", sep=' ')

df2 = df[~((df['TIME'] > 2455788.301) & (df['TIME'] < 2455788.352))] #OOTのところだけをとりだす

time_OOT = np.array(df2['TIME'])
airmass_OOT = np.array(df2['AIRMASS'])
object_flux_OOT = np.array(df2['O_FLUX'])
compa_flux_OOT = np.array(df2['C_FLUX'])

time = np.array(df['TIME'])
airmass = np.array(df['AIRMASS'])
object_flux = np.array(df['O_FLUX'])
compa_flux = np.array(df['C_FLUX'])

# フラックスの計算
# 最適な value を見つける
value_range = np.linspace(-1, 1, 100000)  # 探索する value の範囲
slopes = []
intercepts = []

for value in value_range:
    a,b = axb(value, time_OOT, airmass_OOT, object_flux_OOT, compa_flux_OOT)
    slopes.append(a)
    intercepts.append(b)


min_slope_index = np.argmin(np.abs(slopes))
min_slope_value = value_range[min_slope_index]
min_slope = slopes[min_slope_index]
min_intercept = intercepts[min_slope_index]

print("パラメータの傾きが最小になる value:", min_slope_value)
print("最小傾きのときの傾き (a):", min_slope)
print("最小傾きのときの切片 (b):", min_intercept)





flux = (object_flux / compa_flux) * (10**(airmass * min_slope_value))
flux2 = (object_flux / compa_flux) #比較のために生のの



# 最小二乗法でパラメータを推定


relative_flux = flux / (min_slope* time + min_intercept)
df['RELATIVE'] = relative_flux
df.to_csv(f"/Users/takuto/iriki/GJ1214/A_data/sa.txt", sep=' ', index=False)


# データとフィットラインのプロット
plt.scatter(time, flux, label='Data', alpha=0.5, color='b')
plt.scatter(time, relative_flux, label='Data', alpha=0.5, color='r')
plt.xlabel('Time')
plt.ylabel('Flux')
plt.legend()
plt.show()