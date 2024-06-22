#!/usr/bin/env python3
from pyraf import iraf #sky引き専用
import pandas as pd
import os
iraf.unlearn('imstat')
iraf.imstat.field = 'midpt'
iraf.imstat.nclip = 10

data = pd.read_csv('my_observe_log.csv', delimiter=',')
# object列をインデックスに設定
data.set_index('object', inplace=True)

# 特定のオブジェクトの情報を取得する関数を定義
def get_info(object_name):
    if object_name in data.index:
        row = data.loc[object_name]
        day = row['yymmdd']
        start_file = row['start_file']
        end_file = row['end_file']
        sky_start= row['sky_start']
        sky_end = row['sky_end']

        return f"day={day}, start_file={start_file}, end_file={end_file}, sky_start={sky_start}, sky_end={sky_end}"
    else:
        return "Object not found"

object_name = input("目標天体名を入力してください: ")
row = data[data.index == object_name]

if not row.empty:
    day = row['yymmdd'].values[0]
    start_file = row['start_file'].values[0]
    end_file = row['end_file'].values[0]
    sky_start = row['sky_start'].values[0]
    sky_end = row['sky_end'].values[0]

os.chdir(object_name)
a = []
band_list = ['j', 'h', 'k']
for band in band_list:
    for i in range(int(sky_start), (int(sky_end) + 1) ):
        origin_image = "{}{}-{:04d}.fits".format(band, day, i)
        if not os.path.exists(origin_image):
            print("File {} does not exist. Skipping.".format(origin_image))
            continue
        cut_image = "sky{}{}-{:04d}.fits".format(band, day, i)

        iraf.imcopy(origin_image + "[10:328,10:265]", cut_image)
        result = iraf.imstat(image=cut_image, fields='midpt', nclip=10, Stdout=1)
        midpoint = float(result[1])  # Assuming midpt is the second value in the imstat output
        a.append(midpoint)
        iraf.imarith(cut_image, '-', midpoint, cut_image)



    for i in range(int(start_file), (int(end_file) + 1) ):
        origin_image = "{}{}-{:04d}.fits".format(band, day, i)
        if not os.path.exists(origin_image):
            print("File {} does not exist. Skipping.".format(origin_image))
            continue
        cut_image = "observe{}{}-{:04d}.fits".format(band, day, i)

        iraf.imcopy(origin_image + "[10:328,10:265]", cut_image)



    # 画像の結合を実行
    iraf.imcomb(input="sky{}{}-*.fits".format(band, day), output=f'SKY_{object_name}_{"{}".format(band)}.fits', combine="median", scale="none") #dith9をfusion


    for i in range(int(start_file), (int(end_file) + 1) ):
        iraf.imarith("observe{}{}-{:04d}.fits".format(band, day, i), '-', f'SKY_{object_name}_{"{}".format(band)}.fits', "observe{}{}-{:04d}.fits".format(band, day, i)) #測光したい画像からスカイを引く



















