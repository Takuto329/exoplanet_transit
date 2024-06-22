#!/usr/bin/env python3
from pyraf import iraf
from iraf import noao
from iraf import digiphot
from iraf import apphot
from iraf import images
import matplotlib.pyplot as plt
import math
import os
import pandas as pd

object_name = input("目標天体名を入力してください: ")


iraf.unlearn('apphot')  # パラメータの初期化
iraf.apphot.datapars.datamax = 20000
iraf.apphot.datapars.readnoise = 30
iraf.apphot.datapars.epadu = 8
iraf.apphot.findpars.threshold = 7
iraf.apphot.findpars.sharphi = 0.8
iraf.apphot.daofind.interac = 'no'
iraf.apphot.daofind.verify = 'no'
iraf.apphot.datapars.fwhmpsf = 3
iraf.apphot.centerpars.cbox = 5
iraf.apphot.fitskypars.annulus = 17 #自動で設定したい
iraf.apphot.fitskypars.dannulus = 5 #自動で設定したい
iraf.apphot.photpars.apertures = 15 #自動で設定したい
iraf.apphot.phot.interactive = 'no'
iraf.apphot.phot.verify = 'no'
iraf.apphot.phot.verbose = 'no'
iraf.apphot.photpars.zmag = 0
iraf.imstat.lower = '-1000'
iraf.imstat.upper = '20000'
iraf.imstat.nclip = 10
iraf.imstat.lsigma = 3
iraf.imstat.usigma = 3
iraf.imstat.binwidth = 0.1
iraf.imstat.fields = 'sum,area'
iraf.imstat.format = 'yes'
iraf.imstat.cache = 'yes'
iraf.unlearn('imstat')
iraf.imstat.field = 'mean'
iraf.imstat.nclip = 3


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
        x_center = row['X_center']
        y_center = row['Y_center']


        return f"day={day}, start_file={start_file}, end_file={end_file},x_center={x_center}, y_center={y_center}"
    else:
        return "Object not found"




 #object_name に対応する行を取得
row = data[data.index == object_name]
os.chdir(object_name)
if not row.empty:
    day = row['yymmdd'].values[0]
    start_file = row['start_file'].values[0]
    end_file = row['end_file'].values[0]
    x_center = row['X_center'].values[0]
    y_center = row['Y_center'].values[0]
    with open('1.coo', 'w') as file:
        file.write(f"{x_center} {y_center}\n")

    for i in range(start_file, end_file + 1):
        # ファイル名を生成 (h + day + "-" + i のフォーマット)
        myimage = "observej{}-{:04d}.fits".format(day, i)
        if not os.path.exists(myimage):
            print("File {} does not exist. Skipping.".format(myimage))
            continue

        output = "{:04d}.mag".format(i)  # 出力ファイル名を変更
        iraf.phot(myimage, coords= '1.coo', output=output)
        iraf.imget(myimage, "JD")
        ier = iraf.imget.value
        ier = float(ier)
        JD_value = ier - 2400000
        output_filename = "JD{:04d}.mag".format(i)
        with open(output_filename, 'w') as file:
            file.write(str(JD_value))


for i in range(start_file, end_file):

    mag_file = "{:04d}.mag".format(i)
    center = "C{:04d}.mag".format(i)
    if not os.path.exists(mag_file):
        print("File {} does not exist. Skipping.".format(mag_file))
        continue
    a_save, b_save, c_save, d_save, ab_save = '0', '0', '0', '0', '0'

    try:
        with open(mag_file, 'r') as file:
            lines = file.readlines()
            if lines:
                line = lines[76].split()
                a_save, b_save = line[0], line[1]
                x_center = row['X_center'].values[0]
                x_center = float(x_center)
                a_save = float(a_save)
                a2_save = x_center - a_save
                y_center = row['Y_center'].values[0]
                y_center = float(y_center)
                b_save = float(b_save)
                b2_save = y_center - b_save
                ab_save = math.sqrt(a2_save**2 + b2_save**2)

    except FileNotFoundError:
        pass

    with open(center, 'w') as file:
        file.write(f"{a2_save} {b2_save}\n{ab_save}")



X = []
Y1 = []
Y2 = []
Y3 = []

for i in range(start_file, end_file):
    mag_file = "C{:04d}.mag".format(i)
    JD_file = "JD{:04d}.mag".format(i)
    if not os.path.exists(mag_file):
        print("File {} does not exist. Skipping.".format(mag_file))
        continue
    if not os.path.exists(JD_file):
        print("File {} does not exist. Skipping.".format(JD_file))
        continue
    a2_save, b2_save, c2_save, d2_save, ab_save = '0', '0', '0', '0', '0'
    JD_save = '0'

    try:
        with open(mag_file, 'r') as file:
            lines = file.readlines()
            if lines:
                line = lines[0].split()
                a2_save, b2_save = line[0], line[1]
                line = lines[1].split()
                ab_save = line[0]
    except FileNotFoundError:
        pass

    try:
        with open(JD_file, 'r') as file:
            JD_save = file.read()
    except FileNotFoundError:
        pass

    X.append(float(JD_save))
    Y1.append(float(a2_save))
    Y2.append(float(b2_save))
    Y3.append(float(ab_save))



# データの散布図をプロット
plt.plot(X, Y1, label='X', color='blue', marker = '+', linewidth=1)
plt.plot(X, Y2, label='Y', color='red', marker = '+', linewidth=1)
plt.plot(X, Y3, label='Z', color='green', marker = '+', linewidth=1)

# グラフのラベル
plt.xlabel('X')
plt.ylabel('Y')
plt.title(object_name)
plt.legend()
plt.grid(True)
plt.ylim(-5, 5)
plt.savefig(f'centroid_{object_name}.png', dpi=300)


directory = os.getcwd()

#ディレクトリ内のファイルを取得してループ処理
for filename in os.listdir(directory):
    if filename.endswith(".mag"):
        file_path = os.path.join(directory, filename)
        os.remove(file_path)
