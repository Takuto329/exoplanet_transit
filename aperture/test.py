from pyraf import iraf
from iraf import noao
from iraf import digiphot
from iraf import apphot
from iraf import images

iraf.unlearn('apphot')  
iraf.apphot.fitskypars.annulus = annulus
iraf.apphot.fitskypars.dannulus = dannulus
iraf.apphot.photpars.apertures = 22
iraf.apphot.phot.interactive = 'no'
iraf.apphot.phot.verify = 'no'
iraf.apphot.phot.verbose = 'no'
iraf.apphot.photpars.zmag = 0
date    =   240128
start_file  =   551
end_file	=   724
sky_start_file	=   725
sky_end_file	=   734
all_start_file	=   551
all_end_file	=   734
aperture =   23
annulus =   50
dannulus	=   10


object = 'GJ1214'
image_path = f"/Users/takuto/iriki/{object}/reduction_image"
object_path = f"/Users/takuto/iriki/{object}/config_file/object.coo"
compa_path = f"/Users/takuto/iriki/{object}/config_file/compa.coo"
object_output_path = f"/Users/takuto/iriki/{object}/data/object_value.txt"
compa_output_path = f"/Users/takuto/iriki/{object}/data/compa_value.txt"

for files in range(start_file,end_file+1):

    image = f"{image_path}/jf{files:04d}.fits" 
    iraf.phot(image, coords=object_path, output=object_output_path) #目標星の測光
    object_flux_data = iraf.pdump(object_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでmagをとってくる
    object_flux = float(object_flux_data[0].strip())
 
    iraf.phot(image, coords=compa_path, output=compa_output_path) #比較星の測光
    compa_flux_data = iraf.pdump(compa_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでmagをとってくる
    compa_flux = float(compa_flux_data[0].strip())
    
    flux = object_flux / compa_flux #fluxを割って相対的にする
    print(flux)