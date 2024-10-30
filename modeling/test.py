
import numpy as np
import pandas as pd
from scipy.optimize import minimize
data = pd.read_csv("/Users/takuto/iriki/GJ1214/A_data/T.txt",delimiter=' ')


time = data['TIME']
flux = data['FLUX']
airmass = data['AIRMASS']
x = data['X']
y = data['Y']
# 例として使うデータ（実際のデータに置き換えてください）
Fobs = np.array(flux)  # 分光光度曲線の例
time = np.array(time)  # 時間データの例
airmass = np.array(airmass)  # 大気質データの例
dx = np.array(x)  # x方向の重心位置差の例
dy = np.array(y)  # y方向の重心位置差の例

# 修正関数を定義する
def Fcor(Fobs, k0, kt, kz, kx, ky, time, airmass, dx, dy):
    Δmcor = k0 + kt * time + kz * airmass + kx * dx + ky * dy
    return Fobs * 10**(-0.4* Δmcor)

# パラメータの初期値
initial_guess = np.array([0.1, 0.1, 0.1, 0.1, 0.1])

# scipy.optimize.minimizeを使ってRMSを最小化する
result = minimize(rms_correction, initial_guess, args=(Fobs, time, airmass, dx, dy))

# 最適化されたパラメータを取得する
optimized_params = result.x
print("最適化されたパラメータ:", optimized_params)

# 最小化されたRMS値を表示する（オプション）
minimized_rms = result.fun
print("最小化されたRMS:", minimized_rms)