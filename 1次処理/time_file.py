#!/usr/bin/env python3
from pyraf import iraf #sky引き専用
import pandas as pd
import os
from datetime import datetime, timedelta
iraf.unlearn('imstat')
iraf.imstat.field = 'mode'
iraf.imstat.nclip = 3

object_name = input("目標天体名を入力してください: ")
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


row = data[data.index == object_name]

if not row.empty:
    day = row['yymmdd'].values[0]
    start_file = row['start_file'].values[0]
    end_file = row['end_file'].values[0]
    sky_start = row['sky_start'].values[0]
    sky_end = row['sky_end'].values[0]

os.chdir(object_name)

oot_first = input("トランジットの開始時間(最初のOOTの終わり)をhh:mmで入力してください:")
oot_second = input("トランジットの終了時間(最後のOOTの始まり)をhh:mm+1分で入力してください:")

file = []
for i in range(start_file, end_file + 1):
    myimage = "j{}-{:04d}.fits".format(day, i)
    if not os.path.exists(myimage):
        print("File {} does not exist. Skipping.".format(myimage))
        continue
    iraf.imget(myimage, "JST")
    time_str = iraf.imget.value
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    formatted_time = time_obj.strftime("%H:%M")

    if formatted_time == oot_first:
        file.append(myimage)
        print(myimage)


    if formatted_time == oot_second:
        file.append(myimage)
        print(myimage)




