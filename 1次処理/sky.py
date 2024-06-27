from pyraf import iraf
import pandas as pd
import os
iraf.unlearn('imstat')
iraf.imstat.field = 'midpt'
iraf.imstat.nclip = 10

object = input("star_data(e.g.GJ3470_240128):")
# object = 'GJ1214'

#configファイルから各種パラメータをとってくる
config_path = f"/Users/takuto/iriki/{object}/config_file/config.txt"
config = pd.read_csv(config_path, delimiter='\t')
data = pd.DataFrame(config)

date = data.loc[data['parameter'] == 'date', 'value'].values[0]
start_file = int(data.loc[data['parameter'] == 'start_file', 'value'].values[0])
end_file = int(data.loc[data['parameter'] == 'end_file', 'value'].values[0])
sky_start_file = int(data.loc[data['parameter'] == 'sky_start_file', 'value'].values[0])
sky_end_file = int(data.loc[data['parameter'] == 'sky_end_file', 'value'].values[0])
all_start_file = int(data.loc[data['parameter'] == 'all_start_file', 'value'].values[0])
all_end_file = int(data.loc[data['parameter'] == 'all_end_file', 'value'].values[0])


#パスの指定
raw_image_path = f"/Users/takuto/iriki/{object}/raw_image"
reduction_image_path = f"/Users/takuto/iriki/{object}/reduction_image"
sky_image_path = f"/Users/takuto/iriki/{object}/sky_image"
flat_image_path = f"/Users/takuto/iriki/flat_image"



for band in ['g','i','j', 'h', 'k']:
#---------------------------------------------------------------------------------------------------------------
    # #すべての画像をフラットで割る
    for all_files in range(all_start_file,all_end_file+1):

        raw_image = f"{raw_image_path}/{band}{date}-{all_files:04d}.fits"

        if not os.path.exists(raw_image):
            print("File {} does not exist. Skipping.".format(raw_image))
            continue

        reduction_image = f"{reduction_image_path}/{band}{date}-{all_files:04d}.fits"

        
        iraf.imarith(raw_image, '/', f'{flat_image_path}/{band}flat.fits', reduction_image) #ここで割ってる
#---------------------------------------------------------------------------------------------------------------
    #skyを作る
    sky = []
    for sky_files in range(sky_start_file,sky_end_file+1):

        image = f"{reduction_image_path}/{band}{date}-{sky_files:04d}.fits"
        # image = f"{reduction_image_path}/{band}f{sky_files:04d}.fits" #GJ1214をするとき用(廃線みたいでいいね)

        if not os.path.exists(image):
            print("File {} does not exist. Skipping.".format(image))
            continue

        sky.append(image)
    sky_input = ",".join(sky)
    iraf.imcomb(input=sky_input, output=f'{sky_image_path}/SKY_{band}.fits', combine="median", scale="none") 
#---------------------------------------------------------------------------------------------------------------
    #skyを引く
    for raw_files in range(start_file,end_file+1):
        reduction_image = f"{reduction_image_path}/{band}{date}-{raw_files:04d}.fits"
        # reduction_image = f"{reduction_image_path}/{band}f{raw_files:04d}.fits" #GJ1214をするとき用(廃線みたいでいいね)

        if not os.path.exists(reduction_image):
            print("File {} does not exist. Skipping.".format(reduction_image))
            continue

        iraf.imarith(reduction_image, '-', f'{sky_image_path}/SKY_{band}.fits', reduction_image) #測光したい画像からスカイを引く
#---------------------------------------------------------------------------------------------------------------        
        



















