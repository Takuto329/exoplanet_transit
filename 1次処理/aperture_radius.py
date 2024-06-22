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
band_list = ['j', 'h', 'k']
for band in band_list:

    rms_value = []
    chon = [ap for ap in range(16, 24 + 1)]
    for aperture in chon:
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
        iraf.apphot.fitskypars.annulus = float('{}'.format(aperture)) + 5
        iraf.apphot.fitskypars.dannulus = 10
        iraf.apphot.photpars.apertures = '{}'.format(aperture)
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



        showcom = []
        for i in range(start_file, end_file + 1):
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

            # center = "A{}{:04d}.mag".format(band, i)
            a_save = '0'

            try:
                with open(output, 'r') as file:
                    lines = file.readlines()
                    if lines:


                        line2 = lines[84].split()
                        b_save = line2[3]
                        b_save = float(b_save) * 10 ** -4

                        line3 = lines[89].split()
                        c_save = line3[3]
                        c_save = float(c_save) * 10 ** -4


                        D = (b_save / c_save)


                        showcom.append(D)



            except FileNotFoundError:
                pass

        std_score = np.std(showcom)
        print(std_score)
        # avarage = sum(showcom) / len(showcom)
        # rms = math.sqrt(avarage)
        # print(rms)
        # rms_value.append(rms)

        directory = os.getcwd()

        # ディレクトリ内のファイルを取得してループ処理
        for filename in os.listdir(directory):
            if filename.endswith(".mag"):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)






    # e = []
    # for y in range (0, 3):
    #     la = sorted(rms_value)[y]
    #     count = rms_value.index(la)
    #     e.append(count)
    #     print(int(chon[count]) + 1)
    #
    # with open(f'aperture_radius_{object_name}_{"{}".format(band)}.txt', 'w') as file:
    #     file.write(str(e))
        

    # min_rms = min(std_score)
    # count = rms_value.index(min_rms)
    # with open(f'aperture_radius_{object_name}_{"{}".format(band)}.txt', 'w') as file:
    #     file.write(f"{(chon[count]) + 1}")
    #
    # print(int(chon[count]) + 1) #この出力された数値がootが最小rmsになるアパーチャー半径












