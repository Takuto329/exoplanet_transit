#%%
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
flux = df['FLUX'].values  # フラックス
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
    rp, t0, a = theta
    temp_params = copy.deepcopy(params)
    temp_params.rp = rp
    temp_params.t0 = t0
    temp_params.a = a
    model_flux = model(temp_params, time)
    return -0.5 * np.sum(((flux - model_flux) / flux_err) ** 2)

# 対数事前分布
def ln_prior(theta):
    rp, t0, a = theta
    if 0.01 < rp < 10.0 and min(time) < t0 < max(time) and 5.0 < a < 30.0:  # 軌道長半径の範囲を指定
        return 0.0
    return -np.inf

# 対数事後分布
def ln_posterior(theta, time, flux, flux_err):
    lp = ln_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + ln_likelihood(theta, time, flux, flux_err)

# 初期パラメータ設定
initial = np.array([0.1, np.median(time), 15.0])  # rp, t0, a の初期値
ndim, nwalkers = 3, 50  # パラメータが3つになったので ndim = 3
pos = initial + 1e-4 * np.random.randn(nwalkers, ndim)

# MCMCサンプリング
sampler = emcee.EnsembleSampler(nwalkers, ndim, ln_posterior, args=(time, flux, flux_err))
sampler.run_mcmc(pos, 1000, progress=True)

# MCMCの結果を取得
samples = sampler.get_chain(discard=100, thin=15, flat=True)

# 最適なパラメータ (平均値) を使ってトランジットモデルを計算
best_fit_rp = np.mean(samples[:, 0])
best_fit_t0 = np.mean(samples[:, 1])
best_fit_a = np.mean(samples[:, 2])
params.rp = best_fit_rp
params.t0 = best_fit_t0
params.a = best_fit_a

# フィッティング結果を表示
print(f"最適なパラメータ: ")
print(f"惑星半径の比率 (rp): {best_fit_rp}")
print(f"トランジット中心時間 (t0): {best_fit_t0}")
print(f"軌道長半径 (a): {best_fit_a}")

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
fig = corner.corner(samples, labels=["rp", "t0", "a"])
plt.show()

samples = sampler.get_chain(flat=False)  # デフォルトのflat=Falseを明示的に設定

# パラメータごとにトレースプロットを描画
plt.figure(figsize=(10, 7))

# f_Rpのプロット
plt.subplot(3, 1, 1)
for i in range(samples.shape[1]):  # 各ウォーカーについてプロット
    plt.plot(samples[:, i, 0], 'k', alpha=0.3)
plt.ylabel("rp")
plt.title("Trace Plot of rp")

# f_albedoのプロット
plt.subplot(3, 1, 2)
for i in range(samples.shape[1]):
    plt.plot(samples[:, i, 1], 'k', alpha=0.3)
plt.ylabel("t0")
plt.title("Trace Plot of t0")

# f_InclinationAngle_degのプロット
plt.subplot(3, 1, 3)
for i in range(samples.shape[1]):
    plt.plot(samples[:, i, 2], 'k', alpha=0.3)
plt.ylabel("a")
plt.title("Trace Plot of a")
plt.xlabel("Step number")