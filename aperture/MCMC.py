import batman
import numpy as np
import emcee
import matplotlib.pyplot as plt
import pandas as pd
import corner
import copy

# データの読み込み
df = pd.read_csv("/Users/takuto/iriki/GJ1214/A_data/sa.txt", delim_whitespace=True)
time = df['TIME'].values  # 観測時間
flux = df['RELATIVE'].values  # フラックス
flux_err = np.ones_like(flux) * 0.01  # フラックスの誤差 (仮定値)

# Transitパラメータの設定
params = batman.TransitParams()
params.t0 = np.median(time)  # トランジット中心の初期値
params.per = 1.0  # 周期 (仮定)
params.rp = 0.1  # 初期値
params.a = 15.0  # 軌道長半径の初期値
params.inc = 87.0  # 軌道傾斜角
params.limb_dark = "quadratic"  # リム暗化モデル
params.u = [0.1, 0.3]  # リム暗化パラメータ
params.ecc = 0.0  # 離心率
params.w = 90.0  # 近点引数

# モデル定義
def model(params, time):
    m = batman.TransitModel(params, time)
    return m.light_curve(params)

# 対数尤度関数
def ln_likelihood(theta, time, flux, flux_err):
    rp, t0, r_a = theta  # r_a は R_*/a
    temp_params = copy.deepcopy(params)
    temp_params.rp = rp
    temp_params.t0 = t0
    temp_params.a = 1.0 / r_a  # R_*/a から a を計算
    model_flux = model(temp_params, time)
    return -0.5 * np.sum(((flux - model_flux) / flux_err) ** 2)

# 対数事前分布
def ln_prior(theta):
    rp, t0, r_a = theta
    if 0.01 < rp < 1.0 and min(time) < t0 < max(time) and 0.05 < r_a < 0.2:  # r_a の範囲を設定
        return 0.0
    return -np.inf

# 対数事後分布
def ln_posterior(theta, time, flux, flux_err):
    lp = ln_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + ln_likelihood(theta, time, flux, flux_err)

# 初期パラメータ設定
initial = np.array([0.1, np.median(time), 1.0 / 15.0])  # rp, t0, R_*/a の初期値
ndim, nwalkers = 3, 50  # パラメータが3つになったので ndim = 3
pos = initial + 1e-4 * np.random.randn(nwalkers, ndim)

# MCMCサンプリング
sampler = emcee.EnsembleSampler(nwalkers, ndim, ln_posterior, args=(time, flux, flux_err))
sampler.run_mcmc(pos, 1000, progress=True)

# MCMCの結果を取得
samples = sampler.get_chain(discard=100, thin=15, flat=True)

# トレースプロットを描画する関数
def plot_trace(sampler, labels):
    fig, axes = plt.subplots(ndim, figsize=(10, 7), sharex=True)
    samples = sampler.get_chain()
    for i in range(ndim):
        ax = axes[i]
        ax.plot(samples[:, :, i], "k", alpha=0.3)
        ax.set_xlim(0, len(samples))
        ax.set_ylabel(labels[i])
    axes[-1].set_xlabel("Step number")
    plt.show()

# パラメータのラベル
labels = ["rp", "t0", "R_*/a"]
plot_trace(sampler, labels)

# 自己相関時間の計算
try:
    tau = sampler.get_autocorr_time()
    print("Autocorrelation time:", tau)
    print("Recommended sample size:", np.max(tau) * 10)
except Exception as e:
    print("Autocorrelation time could not be calculated:", e)

# 最適なパラメータ (平均値) を使ってトランジットモデルを計算
best_fit_rp = np.mean(samples[:, 0])
best_fit_t0 = np.mean(samples[:, 1])
best_fit_r_a = np.mean(samples[:, 2])
params.rp = best_fit_rp
params.t0 = best_fit_t0
params.a = 1.0 / best_fit_r_a  # R_*/a から a を計算

# 最適モデルのライトカーブを生成
model_flux = model(params, time)

# 実際のデータとモデルをプロット
plt.figure(figsize=(10, 6))
plt.plot(time, flux, label="Observed Data")
plt.plot(time, model_flux, color="red", label="Best Fit Model")
plt.xlabel("Time")
plt.ylabel("Flux")
plt.legend()
plt.show()

# コーナープロット
fig = corner.corner(samples, labels=["rp", "t0", "R_*/a"])
plt.show()