#%%
from astropy.io import fits
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def calculate_centroid(fits_file, x_min, x_max, y_min, y_max):
    # FITSファイルを読み込む
    hdul = fits.open(fits_file)
    data = hdul[0].data

    # 指定した範囲のデータを抽出
    region = data[y_min:y_max, x_min:x_max]

    # スカイの明るさに対応するデータの抽出
    sky_brightness = data.flatten()

    # 正規分布にフィッティング
    mu, std = norm.fit(sky_brightness)

    # 5σの範囲を計算し、しきい値を設定
    sigma_5_upper = mu + 5 * std
    threshold = sigma_5_upper
    # print(f"しきい値: {threshold}")

    # 重みを付与するために、しきい値を超える値のみを使用
    weighted_region = np.where(region > threshold, region, 0)

    # 重心を計算
    # 重みが0のピクセルは無視される
    y, x = np.indices(weighted_region.shape)  # y, xのインデックスを作成
    total_intensity = np.sum(weighted_region)  # 全体のカウント値の合計

    # 重心を計算（total_intensityが0の場合を考慮）
    if total_intensity > 0:
        x_center = np.sum(x * weighted_region) / total_intensity
        y_center = np.sum(y * weighted_region) / total_intensity

        # 重心の座標を元の画像の実座標に合わせる
        x_center_global = x_center + 0.5 + x_min
        y_center_global = y_center + 0.5 + y_min

        # print(f"重心の座標: (x: {x_center_global}, y: {y_center_global})")
    else:
        print("重みが付与されたピクセルが存在しませんでした。重心を計算できません。")
        hdul.close()
        return

    

    # ファイルを閉じる
    hdul.close()
    return x_center_global,y_center_global

# 使用例
fits_file = "/Users/takuto/iriki/GJ1214/reduction_image/hf0551.fits"  # 適宜ファイルパスを修正してください
x_min, x_max = 558, 608
y_min, y_max = 473, 525
calculate_centroid(fits_file, x_min, x_max, y_min, y_max)