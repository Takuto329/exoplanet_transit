#!/opt/anaconda3/bin python3
from pyraf import iraf
from iraf import noao
from iraf import digiphot
from iraf import apphot
from iraf import images
import pandas as pd
import os

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
iraf.apphot.fitskypars.annulus = 5
iraf.apphot.fitskypars.dannulus = 10
iraf.apphot.photpars.apertures = 5
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

image_path = "/Users/takuto/Downloads/iriki/Transit/"
myimage = "g240128-0103.fits"

# 実際の画像ファイルのパスを生成
full_image_path = os.path.join(image_path, myimage)

# ファイルの存在を確認する
if not os.path.exists(full_image_path):
    print(f"Error: File '{full_image_path}' not found.")
else:
    try:
        # IRAF の処理を実行する
        iraf.phot(myimage, coords="a.txt", output="4.txt")
    except iraf.IrafError as e:
        print(f"IRAF error: {e}")



