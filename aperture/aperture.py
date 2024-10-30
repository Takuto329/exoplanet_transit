#%%
from pyraf_setting import aperture_object, aperture_compa, calculate_f_and_error
from MJD_AIRMASS import MJD, AIRMASS
from find_centroid import calculate_centroid
import pandas as pd 
import matplotlib.pyplot as plt
import os
import numpy as np



# Object name
object = 'GJ1214'

# Config file path and reading configuration parameters
config_path = f"/Users/takuto/iriki/{object}/config_file/config.txt"
config = pd.read_csv(config_path, delimiter='\t')
data = pd.DataFrame(config)
start_file = int(data.loc[data['parameter'] == 'start_file', 'value'].values[0])
end_file = int(data.loc[data['parameter'] == 'end_file', 'value'].values[0])

# Paths for image and coordinate files
image_path = f"/Users/takuto/iriki/{object}/reduction_image"
object_path = f"/Users/takuto/iriki/{object}/config_file/object.coo"
compa_path = f"/Users/takuto/iriki/{object}/config_file/compa.coo"
object_output_path = f"/Users/takuto/iriki/{object}/data/object_value.txt"
compa_output_path = f"/Users/takuto/iriki/{object}/data/compa_value.txt"

# Lists for storing results
mdj = []
airmass = []
compalation = []
xc = []
yc = []


# Loop over the specified range of FITS files
for files in range(start_file, end_file + 1):
    
    image = f"{image_path}/hf{files:04d}.fits" 

    if not os.path.exists(image):
        print(f"File {image} does not exist. Skipping.")
        continue
    
    # MJD and airmass calculation
    mdj.append(MJD(image))
    airmass.append(AIRMASS(image))

    x,y=calculate_centroid(image, 558, 608, 473, 525)
    

    

    # Aperture photometry for object and comparison star
    object_flux, object_error,x2,y2 = aperture_object(image, object_output_path)
    compa_flux, compa_error = aperture_compa(image, compa_output_path)
    error = calculate_f_and_error(object_flux, object_error,compa_flux, compa_error)
   
    xc.append(x-x2)
    yc.append(y-y2)
    # Ratio of object to comparison star flux
    compalation.append(object_flux / compa_flux)
    
  
results = pd.DataFrame({
    'MJD': mdj,
    'Airmass': airmass,
    'Flux Ratio (Object/Comparison)': compalation,
    'x':xc,
    'y':yc,
    'error':error
})

plt.scatter(mdj,compalation)
plt.show()