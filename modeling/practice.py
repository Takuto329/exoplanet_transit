import os
from glob import glob
import pandas as pd
import numpy as np
from pytransit import MandelAgol
from astropy import units as u

import scipy.optimize as op
import itertools


def transit_model_q(parameters, fix, time, model=MandelAgol()):
 
    k_d,tc_d,k_e,tc_e = parameters
    p_d,a_d,b_d,p_e,a_e,b_e,q1_,q2_ = fix
    
    #compute inclination
    inc_d   = np.arccos(b_d/a_d)
    inc_e   = np.arccos(b_e/a_e)
    #convert q to u
    
    #evaluate the model
    m = 1-(1-model.evaluate(time, k_d, (u1,u2), tc_d, p_d, a_d, inc_d))-(1-model.evaluate(time, k_e, (u1,u2), tc_e, p_e,a_e, inc_e))
    
    return m

def rms(flux,flux_model):
    residual = flux-flux_model
    return np.sqrt(np.mean((residual)**2))

def chisq(flux,flux_model,err):
    residual = flux-flux_model
    return np.sum((residual/err)**2)

def obj (params_full,fix, t, f, err):
    '''
    objective function: chi-squared
    '''
    transit_params=params_full[:4]
    sys_params=params_full[4:]
    
    m = transit_model_q(transit_params, fix,t, model=MandelAgol())
    s = np.dot(sys_use,sys_params)
    
    Tc_d = params_full[1]
    if not (time[0]<Tc_d<data_value-1):
        return np.inf
    
    
    kd = params_full[0]
    
    if not (0 < kd < 1):
        return np.inf
    
    
    return np.sum(((f-s*m)/err)**2)

#BIC = chi2 + num_p * np.log(num_d)
object = 'GJ1214'

#--------------------------------------------------------------
#values come from S.Wang et al.(2017) 
tc_0d  = 7682.2921#pm 0.0023(BJD-2450000)
_Pd   = 4.04982 #pm 0.00017(days)
tc_d  = tc_0d+94*_Pd
_ad   = 0.02145 #semimajor axis (AU)
_Rpd  = 0.772 #pm 0.030 (R_earth)

#from M.Gillon et al.(2017)
_bd   = 0.17 #pm0.11

_Rs = 0.117 #pm 0.0036(Rsun)
k_d = _Rpd/_Rs/u.Rsun.to(u.Rearth)
a_s_d= _ad/_Rs/u.Rsun.to(u.au)

u1 = 1
u2 = 2
#--------------------------------------------------------------


df = pd.read_csv(f"/Users/takuto/iriki/{object}/{object}_data.txt", delimiter=',', parse_dates=True)
data_value = len(df)


free=[['TIME'],['SKY'],['AIRMASS'],['dx'],['dy']]

seq1=['TIME','SKY','AIRMASS','dx','dy']
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
df['TIME']=df['TIME']-time_mean

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


w_before = []
sys_combination_OOT = [] 
for n in range(len(free)):
    X=np.ones_like(time_OOT)
    for m in range(len(free[n])):
        X=np.c_[X,df2[free[n][m]]]
    sys_combination_OOT.append(X)
    w = np.linalg.solve(np.dot(X.T,X), np.dot(X.T, flux_OOT))
    w_before.append(w)


time = df['time']

flux = df['flux(13)']
err  = df['err(13)']
    
dx   = df['dx']
dy   = df['dy']
airmass = df['airmass']
sky     = df['sky']

transit_params     = [k_d,tc_d]


sys_use = sys_combination[13]
w = w_before[13]

#combine optimized transit params and sys params
full_params = np.concatenate((transit_params, w), axis=0)
print(full_params)






