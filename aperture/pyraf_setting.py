#%%
from pyraf import iraf
from iraf import noao
from iraf import digiphot
from iraf import apphot
from iraf import images
import numpy as np
from yy import find_optimal_aperture_radius

def calculate_f_and_error(object_flux,object_error,compa_flux,compa_error):
    total_error = np.sqrt((object_error/compa_flux)**2 + (object_flux*compa_error/compa_flux**2)**2)
    return total_error


def aperture_object(image_path,object_output_path):
    object_path = '/Users/takuto/iriki/GJ1214/config_file/object.coo'
    x,y=find_optimal_aperture_radius(image_path,object_path,x_start=558, x_end=608, y_start=473, y_end=525)
    iraf.unlearn('apphot')  
    iraf.apphot.fitskypars.annulus = 50
    iraf.apphot.fitskypars.dannulus = 10
    iraf.apphot.photpars.apertures = 22
    iraf.apphot.phot.interactive = 'no'
    iraf.apphot.phot.verify = 'no'
    iraf.apphot.phot.verbose = 'no'
    iraf.apphot.photpars.zmag = 0


    iraf.phot(image_path, coords=object_path, output=object_output_path)

    object_flux_data = iraf.pdump(object_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでFlux
    object_error_data = iraf.pdump(object_output_path, fields="merr",expr="yes",Stdout=1) #pdumpでFlux

    object_flux = float(object_flux_data[0].strip())
    object_error = float(object_error_data[0].strip()) * object_flux / 1.0857

    return object_flux,object_error,x,y






def aperture_compa(image_path,compa_output_path):
    compa_path = '/Users/takuto/iriki/GJ1214/config_file/compa.coo'
    find_optimal_aperture_radius(image_path,compa_path,x_start=403, x_end=440, y_start=126, y_end=162)
    iraf.unlearn('apphot')  
    iraf.apphot.fitskypars.annulus = 50
    iraf.apphot.fitskypars.dannulus = 10
    iraf.apphot.photpars.apertures = 22
    iraf.apphot.phot.interactive = 'no'
    iraf.apphot.phot.verify = 'no'
    iraf.apphot.phot.verbose = 'no'
    iraf.apphot.photpars.zmag = 0

    iraf.phot(image_path, coords=compa_path, output=compa_output_path)

    compa_flux_data = iraf.pdump(compa_output_path, fields="FLUX",expr="yes",Stdout=1) #pdumpでFlux
    compa_error_data = iraf.pdump(compa_output_path, fields="merr",expr="yes",Stdout=1) #pdumpでFlux

    compa_flux = float(compa_flux_data[0].strip())
    compa_error = float(compa_error_data[0].strip()) * compa_flux / 1.0857

    return compa_flux,compa_error




# file_path = '/Users/takuto/iriki/GJ1214/reduction_image/hf0551.fits'
# compa_output_path = f"/Users/takuto/iriki/GJ1214/data/compa_value.txt"
# object_output_path = f"/Users/takuto/iriki/GJ1214/data/compa_value.txt"
# optimal_radius,b = aperture_compa(file_path,compa_output_path)

# print(b)
