#!/usr/bin/env python3
from pyraf import iraf
from iraf import noao
from iraf import digiphot
from iraf import apphot
from iraf import images
from astropy.io import fits
import pandas as pd 
import os
import matplotlib.pyplot as plt


object = input("star_data(e.g.240128):")

#configファイルから各種パラメータをとってくる
config_path = f"/Users/takuto/iriki/{object}/config.txt"
config = pd.read_csv(config_path, delimiter='\t')
data = pd.DataFrame(config)

date = data.loc[data['parameter'] == 'date', 'value'].values[0]
start_file = int(data.loc[data['parameter'] == 'start_file', 'value'].values[0])
end_file = int(data.loc[data['parameter'] == 'end_file', 'value'].values[0])
aperture = data.loc[data['parameter'] == 'aperture_radius', 'value'].values[0]
annulus = data.loc[data['parameter'] == 'annulus', 'value'].values[0]
dannulus = data.loc[data['parameter'] == 'dannulus', 'value'].values[0]

#パラメータを決める
iraf.unlearn('apphot')  
iraf.apphot.datapars.datamax = 20000
iraf.apphot.datapars.readnoise = 30
iraf.apphot.datapars.epadu = 8
iraf.apphot.findpars.threshold = 7
iraf.apphot.findpars.sharphi = 0.8
iraf.apphot.daofind.interac = 'no'
iraf.apphot.daofind.verify = 'no'
iraf.apphot.datapars.fwhmpsf = 3
iraf.apphot.centerpars.cbox = 5
iraf.apphot.fitskypars.annulus = annulus
iraf.apphot.fitskypars.dannulus = dannulus
iraf.apphot.photpars.apertures = aperture
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


#パスの指定
image_path = f"/Users/takuto/iriki/{object}/data"

object_path = f"/Users/takuto/iriki/{object}/object.coo"
compa_path = f"/Users/takuto/iriki/{object}/compa.coo"

object_output_path = f"/Users/takuto/iriki/{object}/object_value.txt"
compa_output_path = f"/Users/takuto/iriki/{object}/compa_value.txt"


#解析
FLUX = []
TIME = []
for files in range(start_file,end_file+1):

    image = f"{image_path}/g{date}-{files:04d}.fits"

    if not os.path.exists(image):
        print("File {} does not exist. Skipping.".format(image))
        continue


    iraf.phot(image, coords=object_path, output=object_output_path) #目標星の測光
    object_flux_data = iraf.pdump(object_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでFluxをとってくる
    object_flux = float(object_flux_data[0].strip())
    

    iraf.phot(image, coords=compa_path, output=compa_output_path) #比較星の測光
    compa_flux_data = iraf.pdump(compa_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでFluxをとってくる
    compa_flux = float(compa_flux_data[0].strip())

    flux = object_flux / compa_flux #fluxを割って相対的にする
    FLUX.append(flux)


   
    hda = fits.open(image)
    TIME.append(hda[0].header["JD"]) #JDをとってくる
    hda.close()


plt.plot(TIME, FLUX)
plt.xlabel('JD')
plt.ylabel('Flux')
plt.title('qFlux')
plt.grid(True)
plt.show()








    
    




    



    
    



