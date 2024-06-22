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


    iraf.unlearn('apphot')  # パラメータの初期化
    iraf.apphot.datapars.datamax = 20000
    iraf.apphot.datapars.readnoise = 30
    iraf.apphot.datapars.epadu = 8
    iraf.apphot.findpars.threshold = 7
    iraf.apphot.findpars.sharphi = 0.7
    iraf.apphot.daofind.interac = 'no'
    iraf.apphot.daofind.verify = 'no'
    iraf.apphot.datapars.fwhmpsf = 3
    iraf.apphot.centerpars.cbox = 5
    with open(f'aperture_radius_{object_name}_{"{}".format(band)}.txt', 'r') as file:
        aperture = file.readlines()
        line = aperture[0].split()
        aperture_radius = line[0]
        print(aperture_radius)
    iraf.apphot.fitskypars.annulus = float(aperture_radius) + 5
    iraf.apphot.fitskypars.dannulus = 10
    iraf.apphot.photpars.apertures = aperture_radius
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

    JD = []
    for i in range(start_file, end_file + 1):
        JDimage = "j{}-{:04d}.fits".format(day, i)
        if not os.path.exists(JDimage):
            print("File {} does not exist. Skipping.".format(JDimage))
            continue
        JD_value = float(iraf.imget(JDimage, "JD" ,Stdout = 1)) - 2400000
        JD.append(JD_value)



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
        iraf.phot(myimage, coords=coords_file ,output=output)
        a = iraf.imget(output, "Flux" ,Stdout = 1)

        center = "A{}{:04d}.mag".format(band, i)
        a_save = '0'

        try:
            with open(output, 'r') as file:
                lines = file.readlines()
                if lines:
                    line = lines[79].split()
                    a_save = line[3]
                    line2 = lines[84].split()
                    b_save = line2[3]
                    a_save = float(a_save)
                    b_save = float(b_save)
                    c_save = a_save - b_save

        except FileNotFoundError:
            pass

        with open(center, 'w') as file:
            file.write(f"{c_save}")




    X = []
    Y1 = []
    a_save = '0'
    JD_save = '0'
    for i in range(start_file, end_file + 1):

        mag_file = "A{}{:04d}.mag".format(band, i)
        JD_file = "JD{:04d}.mag".format(i)
        if not os.path.exists(mag_file):
            print("File {} does not exist. Skipping.".format(mag_file))
            continue
        if not os.path.exists(JD_file):
            print("File {} does not exist. Skipping.".format(JD_file))
            continue
        a_save = '0'
        JD_save = '0'
        plt.figure()
        try:
            with open(mag_file, 'r') as file:
                lines = file.readlines()
                if lines:
                    line = lines[0].split()
                    a_save = line[0]

        except FileNotFoundError:
            pass

        try:
            with open(JD_file, 'r') as file:
                JD_save = file.read()
        except FileNotFoundError:
            pass

        X.append(float(JD_save))
        Y1.append(float(a_save))

    # データの散布図をプロット
    plt.plot(X, Y1, label='X', color='blue', marker='x', linewidth=1)

    # グラフのラベル
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title("{}_{}".format(object_name, band))
    plt.legend()
    plt.grid(True)
    # plt.ylim(20000, 30000)
    plt.savefig(f'transit_{object_name}_{"{}".format(band)}.png', dpi=300)



    directory = os.getcwd()

    #ディレクトリ内のファイルを取得してループ処理
    for filename in os.listdir(directory):
        if filename.endswith(".mag"):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)

