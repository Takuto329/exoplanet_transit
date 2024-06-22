#!/usr/bin/env python3
import os
object_name = input("目標天体名を入力してください: ")

# ディレクトリのパスを指定
directory = f"/mnt/c/Users/takut/Downloads/iriki/{object_name}"

# ディレクトリ内のファイルを取得してループ処理
for filename in os.listdir(directory):
    if filename.endswith(".mag"):
        file_path = os.path.join(directory, filename)
        os.remove(file_path)

