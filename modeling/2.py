import numpy as np
import pandas as pd

# object = 'GJ1214'
# data_path = f"/Users/takuto/iriki/{object}/A_data/config.txt"
# data = pd.read_csv(data_path, delimiter=' ')

# object_flux = data['FLUX']
# sky_flux = data['SKY']
# airmass = data['AIRMASS']

object_flux = 10000
sky_flux = 5000
airmass = 1.4



def sn(): #SN比を出す関数
    g = 1.19
    D = 140 #望遠鏡の口径
    t = 49 #露出時間
    h = 1029 #標高
    z = airmass
    star = np.sqrt(object_flux/g)
    print(star)
    sky = np. sqrt(sky_flux/g)
    print(sky)

    rscin =  0.064 * object_flux * ((D/2)**(-2/3)) * ((t/1)**(-1/2)) * ((h/8000)**(3/2)) * ((z/(np.cos(np.radians(z))))**(7/4))
    print(rscin)
    N = np.sqrt(star**2+sky**2+rscin**2)
    S = object_flux
    SN = S/N
    
    return SN


print(sn())