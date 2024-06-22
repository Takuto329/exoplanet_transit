#!/usr/bin/env python3
from pyraf import iraf
from iraf import noao
from iraf import digiphot
from iraf import apphot
from iraf import images
import matplotlib.pyplot as plt
import math
import numpy as np
import os
import pandas as pd
object_name = input("目標天体名を入力してください: ")
data = pd.read_csv('my_observe_log.csv', delimiter=',')
data.set_index('object', inplace=True)
def get_info(object_name):
    if object_name in data.index:
        row = data.loc[object_name]
        day = row['yymmdd']
        start_file = row['start_file']
        end_file = row['end_file']
        x_center = row['X_center']
        y_center = row['Y_center']
        cx_center = row['CXcenter']
        cy_center = row['CYcenter']
        Soot = row['Soot']
        Eoot = row['Eoot']

        return f"day={day}, start_file={start_file}, end_file={end_file},x_center={x_center}, y_center={y_center}, cx_center={cx_center}, cy_center={cy_center}, Soot={Soot}, Eoot={Eoot}"
    else:
        return "Object not found"

row = data[data.index == object_name]
if not row.empty:
    day = row['yymmdd'].values[0]
    start_file = row['start_file'].values[0]
    end_file = row['end_file'].values[0]
    x_center = row['X_center'].values[0]
    y_center = row['Y_center'].values[0]
    cx_center = row['CXcenter'].values[0]
    cy_center = row['CYcenter'].values[0]
    Soot = row['Soot'].values[0]
    Eoot = row['Eoot'].values[0]

os.chdir(object_name)

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
iraf.apphot.fitskypars.annulus = 22 #自動で設定したい
iraf.apphot.fitskypars.dannulus = 5 #自動で設定したい
iraf.apphot.photpars.apertures = 11 #自動で設定したい
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

with open('j.coo', 'w') as file:
    file.write(f"{x_center} {y_center}\n{cx_center} {cy_center}\n")

A = 1.7
B = 15.19
xh_center = x_center - A
yh_center = y_center - B
cxh_center = cx_center - A
cyh_center = cy_center - B
with open('h.coo', 'w') as file:
    file.write(f"{xh_center} {yh_center}\n{cxh_center} {cyh_center}\n")

C = 20.23
D = 9.72
xks_center = x_center - C
yks_center = y_center - D
cxks_center = cx_center - C
cyks_center = cy_center - D
with open('ks.coo', 'w') as file:
    file.write(f"{xks_center} {yks_center}\n{cxks_center} {cyks_center}\n")

band_list = ['j', 'h', 'k']
for band in band_list:
    for i in range(start_file, end_file + 1):
        # myimage = "observe{}{}-{:04d}.fits".format(band, day, i)
        myimage = "observe{}{}-{:04d}.fits".format(band, day, i)
        if not os.path.exists(myimage):
            print("File {} does not exist. Skipping.".format(myimage))
            continue

        output = "{}{:04d}.mag".format(band, i)
        if band == 'h':
            coords_file = 'h.coo'
        elif band == 'k':
            coords_file = 'ks.coo'
        else:
            coords_file = 'j.coo'
        iraf.phot(myimage, coords=coords_file, output=output)

        iraf.imget(myimage, "JD")
        ier = iraf.imget.value
        ier = float(ier)
        JD_value = ier - 2400000
        output_filename = "JD{:04d}.mag".format(i)
        with open(output_filename, 'w') as file:
            file.write(str(JD_value))

for band in band_list:
    for i in range(start_file, end_file + 1):
        mag_file = "{}{:04d}.mag".format(band, i)

        center = "A{}{:04d}.mag".format(band, i)
        if not os.path.exists(mag_file):
            print("File {} does not exist. Skipping.".format(mag_file))
            continue
        a_save = '0'

        try:
            with open(mag_file, 'r') as file:
                lines = file.readlines()
                if lines:
                    line = lines[79].split()
                    a_save = line[3]
                    line2 = lines[84].split()
                    b_save = line2[3]
                    a_save = float(a_save)
                    b_save = float(b_save)
        except FileNotFoundError:
            pass

        with open(center, 'w') as file:
            file.write(f"{a_save}\n{b_save}")



X = []
Y1 = []
Y2 = []


band_list = ['j', 'h', 'k']
for band in band_list:
    X = []  # Clear the lists for each band
    Y1 = []
    Y2 = []
    a_save, b_save = '0', '0'
    JD_save = '0'
    for i in range(start_file, end_file):
        mag_file = "A{}{:04d}.mag".format(band, i)
        JD_file = "JD{:04d}.mag".format(i)
        if not os.path.exists(mag_file):
            print("File {} does not exist. Skipping.".format(mag_file))
            continue
        if not os.path.exists(JD_file):
            print("File {} does not exist. Skipping.".format(JD_file))
            continue
        a_save, b_save = '0', '0'
        JD_save = '0'
        plt.figure()
        try:
            with open(mag_file, 'r') as file:
                lines = file.readlines()
                if lines:
                    line = lines[0].split()
                    a_save = line[0]
                    line = lines[1].split()
                    b_save = line[0]
        except FileNotFoundError:
            pass

        try:
            with open(JD_file, 'r') as file:
                JD_save = file.read()
        except FileNotFoundError:
            pass

        X.append(float(JD_save))
        Y1.append(float(a_save))
        Y2.append(float(b_save))

    X_unique = np.unique(X)
    Y1_unique = [Y1[i] for i in range(len(Y1)) if X[i] in X_unique]
    Y2_unique = [Y2[i] for i in range(len(Y2)) if X[i] in X_unique]

    # データの散布図をプロット
    plt.plot(X, Y1, label='X', color='blue', marker='x', linewidth=1)
    plt.plot(X, Y2, label='Y', color='red', marker='x', linewidth=1)


        # グラフのラベル
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title("{}_{}".format(band, object_name))

    plt.legend()
    plt.grid(True)

    plt.savefig(f'photmetry_{object_name}_{"{}".format(band)}.png')




directory = os.getcwd()

#ディレクトリ内のファイルを取得してループ処理
for filename in os.listdir(directory):
    if filename.endswith(".mag"):
        file_path = os.path.join(directory, filename)
        os.remove(file_path)