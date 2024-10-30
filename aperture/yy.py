#%%
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from photutils import CircularAperture, CircularAnnulus, aperture_photometry
import math

def find_optimal_aperture_radius(file_path, output_path,x_start, x_end, y_start, y_end,threshold=None, radii_range=(1, 50, 0.1), annulus_r=40, deanulus_r=10):
    """
    指定されたFITSファイルからデータを読み込み、指定範囲を切り取り、
    外接円の中心を求め、その中心を基準に異なる半径で測光を行い、
    最適なアパーチャー半径を返す。

    Parameters:
    - file_path (str): FITSファイルのパス
    - x_start, x_end (int): x方向の切り取り範囲
    - y_start, y_end (int): y方向の切り取り範囲
    - threshold (float): 二値化のための閾値
    - radii_range (tuple): 測光に使用する半径の範囲（開始、終了、ステップ）
    - annulus_r (int): アニュラスの内側の半径
    - deanulus_r (int): アニュラスの幅

    Returns:
    - optimal_radius (float): 最適なアパーチャー半径
    """
    # FITSファイルを読み込む
    with fits.open(file_path) as hdul:
        data = hdul[0].data

    # 指定した範囲を切り取る
    cut_data = data[y_start:y_end, x_start:x_end]

    # スカイの明るさに対応するデータの抽出
    sky_brightness = data.flatten()

    # 正規分布にフィッティング
    from scipy.stats import norm
    mu, std = norm.fit(sky_brightness)

    # 5σの範囲を計算
    sigma_5_upper = mu + 5 * std
    threshold = sigma_5_upper 
  
    # print(threshold)

    # 二値化処理
    binary_data = (cut_data > threshold).astype(int)

    # 「1」の範囲の座標を取得
    y_coords, x_coords = np.where(binary_data == 1)
    points = np.vstack((x_coords, y_coords)).T

    # 外接円を求める
    if len(points) > 0:
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]

        # 最小外接円を求める
        def minimum_enclosing_circle(points):
            x_coords = points[:, 0]
            y_coords = points[:, 1]
            x_center = np.mean(x_coords)
            y_center = np.mean(y_coords)
            max_distance = 0
            for x, y in points:
                distance = math.sqrt((x - x_center) ** 2 + (y - y_center) ** 2)
                if distance > max_distance:
                    max_distance = distance
            return x_center, y_center, max_distance
        
        # 最小外接円の中心と半径を計算
        center_x, center_y, radius = minimum_enclosing_circle(hull_points)
        center_x += x_start
        center_y += y_start
      
    else:
        raise ValueError("データ内に値が「1」のピクセルがありません。")

    # 外接円の中心座標をファイルに保存
    with open(output_path, 'w') as f:
        f.write(f"{center_x:.2f} {center_y:.2f}\n")
    return center_x,center_y
#     # 測光を行う
#     total_fluxes = []
#     radii_list = np.arange(*radii_range).tolist()
#     for radius in radii_list:
#         # 測光用の円形アパーチャを作成
#         aperture = CircularAperture((centroid_x, centroid_y), r=radius)
#         annulus_aperture = CircularAnnulus((centroid_x, centroid_y), r_in=annulus_r, r_out=annulus_r + deanulus_r)
        
#         # 測光を実行
#         apertures = [aperture, annulus_aperture]
#         phot_table = aperture_photometry(data, apertures)
        
#         # アニュラスの平均値を引く（背景補正）
#         bkg_mean = phot_table['aperture_sum_1'][0] / annulus_aperture.area
#         bkg_flux = bkg_mean * aperture.area
#         flux = phot_table['aperture_sum_0'][0] - bkg_flux
        
#         total_fluxes.append(flux)

#     # エンサークルドエナジーの計算
#     encircled_energy = np.array(total_fluxes) / np.max(total_fluxes)

#     # 最適なアパーチャー半径を見つける（エンサークルドエナジーが90%を超える最小の半径）
    
#     for radius, ee in zip(radii_list, encircled_energy):
#         if ee >= 0.9:
#             optimal_radius = radius
#             break

#     if optimal_radius is None or optimal_radius == 0:
#         raise ValueError("エンサークルドエナジーが90%を超える半径が見つかりませんでした。")

#     return optimal_radius

# # 使用例
# # file_path = '/Users/takuto/iriki/GJ1214/reduction_image/hf0551.fits'

# # x_start=403
# # x_end=440
# # y_start=126
# # y_end=162
# # optimal_radius = find_optimal_aperture_radius(file_path, x_start, x_end, y_start, y_end)
# # print(f"最適なアパーチャー半径: {optimal_radius}")
