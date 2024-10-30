from astropy.io import fits
from astropy.time import Time


def MJD(image):
    
    hdu = fits.open(image)
    if 'MJD' in hdu[0].header:
    # 'MJD' が存在する場合、その値を使用
        MJD = hdu[0].header["MJD"]

    else:
    
        DATE_UTC = hdu[0].header["DATE_UTC"]
        TIME_UTC = hdu[0].header["TIME_UTC"]

    # UTC日時を指定
        datetime_utc = DATE_UTC + ' ' + TIME_UTC

    # astropy.timeを使ってUTC日時をMJDに変換
        time = Time(datetime_utc, format='iso', scale='utc')
        MJD = time.mjd  # .jdではなく.mjdに変更 
        
    hdu.close()
    return MJD



def AIRMASS(image):
    hdu = fits.open(image)
    airmass = float(hdu[0].header["AIRMASS"])
    hdu.close()
    return(airmass)


    