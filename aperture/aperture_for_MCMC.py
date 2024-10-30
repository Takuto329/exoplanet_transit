#%%
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# FITSファイルの読み込み
fits_file = f'/Users/takuto/iriki/GJ1214/reduction_image/hf0551.fits'  # FITSファイルのパスを指定
hdul = fits.open(fits_file)
data = hdul[0].data

# スカイの明るさに対応するデータの抽出
# データの範囲やマスク処理が必要かもしれません
sky_brightness = data.flatten()  # 1次元に変換

# ピクセルデータの分布をプロット
plt.hist(sky_brightness, bins=100, density=True, alpha=0.6, color='g')

# 正規分布にフィッティング
mu, std = norm.fit(sky_brightness)

# フィッティング結果のプロット
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2)
title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
plt.title(title)

# 5σの範囲を計算
sigma_5_lower = mu - 5 * std
sigma_5_upper = mu + 5 * std
print(f"5σの範囲: {sigma_5_lower} 〜 {sigma_5_upper}")

plt.show()