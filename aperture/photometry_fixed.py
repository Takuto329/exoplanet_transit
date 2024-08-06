#!/usr/bin/env python3
from pyraf import iraf
from iraf import noao
from iraf import digiphot
from iraf import apphot
from iraf import images
from astropy.io import fits
from astropy.time import Time
import pandas as pd 
import os
import numpy as np
import datetime
import cv2
from scipy.ndimage import center_of_mass
import matplotlib.pyplot as plt



# object = input("star_data(e.g.240128):")
object = 'GJ1214'

#configファイルから各種パラメータをとってくる
config_path = f"/Users/takuto/iriki/{object}/config_file/config.txt"
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
iraf.apphot.fitskypars.annulus = annulus
iraf.apphot.fitskypars.dannulus = dannulus
iraf.apphot.photpars.apertures = 22
iraf.apphot.phot.interactive = 'no'
iraf.apphot.phot.verify = 'no'
iraf.apphot.phot.verbose = 'no'
iraf.apphot.photpars.zmag = 0



#パスの指定
image_path = f"/Users/takuto/iriki/{object}/reduction_image"
syu_path = f"/Users/takuto/iriki/{object}"

object_path = f"/Users/takuto/iriki/{object}/config_file/object.coo"
compa_path = f"/Users/takuto/iriki/{object}/config_file/compa.coo"

object_output_path = f"/Users/takuto/iriki/{object}/data/object_value.txt"
compa_output_path = f"/Users/takuto/iriki/{object}/data/compa_value.txt"

#-------------------------------------------------------------- 
#マスクの関数 
def create_annulus_mask(shape, center, inner_radius, outer_radius):
    """
    Create a binary mask with an annulus (a ring).
    
    Parameters:
    shape (tuple): Shape of the output mask (height, width).
    center (tuple): Center of the annulus (y, x).
    inner_radius (float): Inner radius of the annulus.
    outer_radius (float): Outer radius of the annulus.
    
    Returns:
    numpy.ndarray: Binary mask with an annulus.
    """
    y, x = np.ogrid[:shape[0], :shape[1]]
    dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    mask = (dist_from_center >= inner_radius) & (dist_from_center <= outer_radius)
    return mask
#-------------------------------------------------------------- 
#解析
FLUX = []
O_FLUX = []
C_FLUX = []
ERROR = []
SKY = []
X = []
Y = []
TIME = []
AIRMASS = []
SA = []


for files in range(start_file,end_file+1):

    # image = f"{image_path}/j{date}-{files:04d}.fits"
    image = f"{image_path}/jf{files:04d}.fits" #GJ1214をするとき用(廃線みたいでいいね)

    if not os.path.exists(image):
        print("File {} does not exist. Skipping.".format(image))
        continue
#--------------------------------------------------------------    
    hdu = fits.open(image)
#--------------------------------------------------------------
    data = hdu[0].data
    x_center, y_center = 580, 495
    radius = 20

    y, x = np.ogrid[:data.shape[0], :data.shape[1]]
    mask = (x - x_center)**2 + (y - y_center)**2 <= radius**2
    masked_data = np.where(mask, data, 0)
    y_centroid, x_centroid = center_of_mass(masked_data)

    x_M = x_center - x_centroid
    y_M = y_center - y_centroid

    X.append(x_M)
    Y.append(y_M)
#--------------------------------------------------------------
    AIRMASS.append(hdu[0].header["AIRMASS"])
#--------------------------------------------------------------    
    # TIME.append(hda[0].header["MJD"]) #JDをとってくる
#--------------------------------------------------------------   
    DATE_UTC = hdu[0].header["DATE_UTC"]
    TIME_UTC = hdu[0].header["TIME_UTC"]

    # UTC日時を指定
    datetime_utc = DATE_UTC + ' ' + TIME_UTC
    
    # astropy.timeを使ってUTC日時をMJDに変換
    time = Time(datetime_utc, format='iso', scale='utc')
    mjd = time.jd
    
    # TIME列にMJDを追加
    TIME.append(mjd)
#--------------------------------------------------------------
    sky_center = (580, 495)  # (y, x)
    inner_radius = 50  # 内半径
    outer_radius = 60  # 外半径

    mask = create_annulus_mask(data.shape, sky_center, inner_radius, outer_radius)
    sky_region = data[mask]
    sky_threshold = np.max(sky_region)

    x_start, x_end = 490, 670
    y_start, y_end = 410, 590

    region = data[y_start:y_end, x_start:x_end]

    binary_region = (region > sky_threshold).astype(int)

    # OpenCVを使用して星を検出し、その中心を求める
    binary_image = (binary_region * 255).astype(np.uint8)  # OpenCVが扱いやすいように変換

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) < 10:
            continue
        (x, y), radius = cv2.minEnclosingCircle(contour)
        xz = x + 490
        yz = y + 410
        with open(object_path, mode='w') as f:
            f.write(str(xz)+' '+str(yz))
 #--------------------------------------------------------------
    sky_center = (420, 147)  # (y, x)
    inner_radius = 50  # 内半径
    outer_radius = 60  # 外半径

    mask = create_annulus_mask(data.shape, sky_center, inner_radius, outer_radius)
    sky_region = data[mask]
    sky_threshold = np.max(sky_region)

    x_start, x_end = 380, 470
    y_start, y_end = 97, 197

    region = data[y_start:y_end, x_start:x_end]

    binary_region = (region > sky_threshold).astype(int)

    # OpenCVを使用して星を検出し、その中心を求める
    binary_image = (binary_region * 255).astype(np.uint8)  # OpenCVが扱いやすいように変換

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) < 10:
            continue
        (x, y), radius = cv2.minEnclosingCircle(contour)
        xz = x + 380
        yz = y + 97
        with open(compa_path, mode='w') as f:
            f.write(str(xz)+' '+str(yz))
 #--------------------------------------------------------------         
    hdu.close()
 #--------------------------------------------------------------
    iraf.phot(image, coords=object_path, output=object_output_path) #目標星の測光
    object_flux_data = iraf.pdump(object_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでmagをとってくる
    sky_data = iraf.pdump(object_output_path, fields="MSKY",expr="yes",Stdout=1)
    object_flux = float(object_flux_data[0].strip())
    sky = float(sky_data[0].strip())
    
    # object_error = 10**((float(object_error_data[0].strip())) / 2.5)
    object_error = 0
    

    iraf.phot(image, coords=compa_path, output=compa_output_path) #比較星の測光
    compa_flux_data = iraf.pdump(compa_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでmagをとってくる
    compa_flux = float(compa_flux_data[0].strip())
    
    

    flux = object_flux / compa_flux #fluxを割って相対的にする



    FLUX.append(flux)
    ERROR.append(object_error)
    O_FLUX.append(object_flux)
    C_FLUX.append(compa_flux)
    SKY.append(sky)
    
    
 #--------------------------------------------------------------
data = {
    'TIME': TIME,
    'FLUX': FLUX,
    'O_FLUX': O_FLUX,
    'C_FLUX': C_FLUX,
    # 'ERROR': ERROR,
    'AIRMASS': AIRMASS,
    'SKY': SKY,
    'dx': X,
    'dy': Y
    
}
df = pd.DataFrame(data)

dt_now = datetime.datetime.now()
# データフレームをテキストファイルに保存
df.to_csv(f"/Users/takuto/iriki/{object}/A_data/sa.txt", index = False, sep=' ')

# plt.scatter(TIME,FLUX,alpha=0.5)
# plt.xlabel('JD')
# plt.ylabel('Flux')
# plt.title('Transit')
# plt.grid(True)
# plt.savefig(f"/Users/takuto/iriki/{object}/A_data/{dt_now}.png")

# plt.scatter(TIME,O_FLUX,alpha=0.5)
# plt.scatter(TIME,C_FLUX,alpha=0.5)
# plt.show()




