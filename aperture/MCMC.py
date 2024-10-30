#%%
import numpy as np
import emcee
import matplotlib.pyplot as plt
import corner
from aperture import results  # この部分はご自身のデータのインポートに応じて変更してください

# データの読み込み
df2 = results[~((results['MJD'] > 55787.81308101852) & (results['MJD'] < 55787.84795833333))]
t = df2['MJD']  # 時間
F_obs = df2['Flux Ratio (Object/Comparison)']  # 観測フラックス
error = df2['error']
z = df2['Airmass']  # エアマス
dx = df2['x']  # x方向の位置変化
dy = df2['y']  # y方向の位置変化

# モデル式
def model(k_z, k_x, k_y):
    delta_m_cor = k_z * z + k_x * dx + k_y * dy
    F_cor = F_obs*10**(-0.4 * delta_m_cor)
    return F_cor

# 尤度関数 (ばらつきを最小化)
def log_likelihood(theta,F_obs,error):
    k_z, k_x, k_y = theta
    correction = model(k_z, k_x, k_y)

    # データを正規化
    F_corrected_normalized = correction / np.mean(correction)

    # 正規化されたデータの分散を最小化
    residuals = F_corrected_normalized -1
    sigma = error
    logL = -0.5 * np.sum((residuals / sigma) ** 2)
    return logL

# パラメータの事前分布
def ln_prior(theta):
    k_z, k_x, k_y = theta
    if -1.0 < k_z < 1.0 and -1.0 < k_x < 1.0 and -1.0 < k_y < 1.0:
        return 0.0
    return -np.inf

# 尤度と事前分布を結合
def log_probability(theta,F_obs,error):
    lp = ln_prior(theta)
    
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta,F_obs,error)

# MCMCの設定
initial = np.array([0.0, 0.0, 0.0])  # 初期値
ndim, nwalkers = 3, 100
pos = initial + 1e-4 * np.random.randn(nwalkers, ndim)

# MCMCの実行
sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=(F_obs,error))
sampler.run_mcmc(pos, 1000, progress=True)

# MCMCの結果を取得
samples = sampler.get_chain(discard=100, thin=15, flat=True)

# コーナープロット
fig = corner.corner(samples, labels=["k_z", "k_x", "k_y"], truths=[0, 0, 0])
plt.show()

# パラメータの最適値 (中央値を使って最適パラメータを決定)
best_params = np.median(samples, axis=0)
print("Best fit parameters: ", best_params)
best_fit_kz = np.median(samples[:, 0])
best_fit_kx = np.median(samples[:, 1])
best_fit_ky = np.median(samples[:, 2])
# フィット結果のプロット (観測データと補正後のデータの比較)
corrected_flux = model(best_fit_kz, best_fit_kx, best_fit_ky)

plt.figure(figsize=(10, 6))
plt.scatter(t, F_obs, label="Observed")
plt.scatter(t, corrected_flux, label="Corrected Data", color="orange")
plt.xlabel("Time")
plt.ylabel("Flux")
plt.legend()
plt.show()
