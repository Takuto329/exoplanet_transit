#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os
import math

object_name = input("目標天体名を入力してください: ")
band = input("バンド名を入力:")

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


numbers_list = []
with open(f'{object_name},{band}.txt', 'r') as file:
    lines = file.readlines()
    for line in lines[0 : int(Soot) - start_file - 1]:
        numbers_list.append(float(line.strip()))

    for line in lines[int(Eoot) - start_file : end_file - start_file - 1]:
        numbers_list.append(float(line.strip()))

    # lines = [file.readline().strip() for _ in range(0, int(Soot) - start_file)]




average = sum(numbers_list) / len(numbers_list)

# 結果の表示



with open(f'{object_name},{band}.txt', 'r') as input_file:
    # ファイルからすべての行を読み込む
    lines = input_file.readlines()



# 各行の数値を2で割る
result_numbers = [str(float(number) / average) for number in lines]

# 結果を新しいファイルに書き込む
# with open(f'{object_name},{band}2.txt', 'w') as output_file:  #何か知らんけどexcelからコピーした数値をtxtファイルに貼り付けたらエラーが出る
#     output_file.writelines(result_numbers)
with open(f'{object_name},{band}2.txt', 'w') as output_file:
    for value in result_numbers:
        output_file.write(value + '\n')


