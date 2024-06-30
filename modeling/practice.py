import batman
import pandas as pd
import numpy as np
import itertools

object = 'GJ1214'


params = batman.TransitParams()
params.t0 = 0.                       #time of inferior conjunction
params.per = 1.                      #orbital period
params.rp = 0.1                      #planet radius (in units of stellar radii)
params.a = 15.                       #semi-major axis (in units of stellar radii)
params.inc = 87.                     #orbital inclination (in degrees)
params.ecc = 0.                      #eccentricity
params.w = 90.                       #longitude of periastron (in degrees)
params.u = [0.1, 0.3]                #limb darkening coefficients [u1, u2]
params.limb_dark = "quadratic"   

t = np.linspace(-0.05, 0.05, 100)

m = batman.TransitModel(params, t)    #initializes model
flux = m.light_curve(params)          #calculates light curve



df = pd.read_csv(f"/Users/takuto/iriki/{object}/{object}_data.txt", delimiter=',', parse_dates=True)
data_value = len(df)


free=[['TIME'],['AIRMASS'],['X'],['Y']]

seq1=['TIME','AIRMASS','X','Y']
temp1=list(itertools.combinations(seq1,1))
temp2=list(itertools.combinations(seq1,2))
temp3=list(itertools.combinations(seq1,3))

m=0
for m in range(len(temp3)):
    b=[seq1[n] for n in range(len(seq1)) if not seq1[n] in temp3[m]]
    free.append(b)
    m += 1
m=0
for m in range(len(temp2)):
    b=[seq1[n] for n in range(len(seq1)) if not seq1[n] in temp2[m]]
    free.append(b)
    m += 1    
m=0
for m in range(len(temp1)):
    b=[seq1[n] for n in range(len(seq1)) if not seq1[n] in temp1[m]]
    free.append(b)
    m += 1

free.append(seq1)


time_mean = (df['TIME'][0]+df['TIME'][data_value-1])/2
df['del_time']=df['TIME']-time_mean

sys_combination = [] 

for n in range(len(free)):
    X=np.ones_like(df['TIME'])
    for m in range(len(free[n])):
        X=np.c_[X,df[free[n][m]]]
    sys_combination.append(X)

print(sys_combination)

df2 = df[~((df['time']>8062.910) & (df['time']< 8063.00))]
time_OOT = df2['time']
flux_OOT = df2['flux(13)']