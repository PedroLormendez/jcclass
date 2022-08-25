#!/usr/bin/env python
# coding: utf-8

# In[1]:
"""
@Author: Pedro Herrera-Lormendez
"""

import numpy as np
import pandas as pd
import xarray as xr

def eleven_CTs(CT):
    '''
    Computes the reduced 11 circulation types based on their advective
    characteristics

    :params CT: DataArray of the 27 circulation types
    '''
    CT = xr.where( (CT == 11) | (CT==21) | (CT ==1), 1, CT) #NE
    CT = xr.where( (CT == 12) | (CT==22) | (CT==2), 2, CT) #E
    CT = xr.where( (CT == 13) | (CT==23) | (CT==3), 3, CT) #SE
    CT = xr.where( (CT == 14) | (CT==24) | (CT==4), 4, CT) #S
    CT = xr.where( (CT == 15) | (CT==25) | (CT==5), 5, CT) #SW
    CT = xr.where( (CT == 16) | (CT==26) | (CT==6), 6, CT) #W
    CT = xr.where( (CT == 17) | (CT==27) | (CT==7), 7, CT) #NW
    CT = xr.where( (CT == 18) | (CT==28) | (CT==8), 8, CT) #N
    # CT = xr.where(CT == -1, 0, CT)
    # CT = xr.where(CT ==  0, 10, CT)
    CT = xr.where(CT == 20, 9, CT) #C
    return(CT)

# def seasonal_frelative_frequencies(CTs_11, year_init, year_end):
#     '''
#     This function computes the climatological seasonal relative frequencies 
#     of the JK derived 11 CTs

#     :param CTs_11: DataArray of the reduced eleven circulation types
#     :year_init   : str Starting year to computer the climatology
#     :year_end    : str Ending year to compute the climatology
    
#     '''
#     #Reading the daily CTs dataset
#     CT = DS.CT.sel(time = slice(str(year_init)+'-03-01', str(year_end)+'-11-30'))
#     del(DS)
#     LF = xr.where(CT == -1, 1, np.nan)
#     A = xr.where(CT ==  0, 1, np.nan)
#     C = xr.where(CT == 20, 1, np.nan)
#     NE = xr.where( (CT == 11) | (CT==21) | (CT ==1), 1, np.nan)
#     E = xr.where( (CT == 12) | (CT==22) | (CT==2), 1, np.nan)
#     SE = xr.where( (CT == 13) | (CT==23) | (CT==3), 1, np.nan)
#     S = xr.where( (CT == 14) | (CT==24) | (CT==4), 1, np.nan)
#     SW = xr.where( (CT == 15) | (CT==25) | (CT==5), 1, np.nan)
#     W = xr.where( (CT == 16) | (CT==26) | (CT==6), 1, np.nan)
#     NW = xr.where( (CT == 17) | (CT==27) | (CT==7), 1, np.nan)
#     N = xr.where( (CT == 18) | (CT==28) | (CT==8), 1, np.nan)
#     month_length = CT.time.dt.days_in_month
#     len_seasons=month_length.resample(time = '1M').mean().resample(time = 'Q-FEB').sum()
#     # weights = month_length.groupby('time.season') / month_length.groupby('time.season').sum()
#     LF_seasons = ((LF.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')

#     A_seasons   = ((A.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')

#     C_seasons   = ((C.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')

#     N_seasons  = ((N.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
#     NE_seasons = ((NE.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
#     E_seasons  = ((E.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
#     SE_seasons = ((SE.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
#     S_seasons  = ((S.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
#     SW_seasons = ((SW.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
#     W_seasons  = ((W.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
#     NW_seasons = ((NW.resample(time = 'Q-FEB').sum() / len_seasons) *100).groupby('time.season').mean(dim = 'time')
    
#     CTs = {'LF':LF_seasons, 
#        'A': A_seasons, 
#       'C':C_seasons, 
#       'NE':NE_seasons, 'E':E_seasons, 'SE':SE_seasons, 'S':S_seasons, 'SW':SW_seasons, 'W':W_seasons, 'NW':NW_seasons, 'N':N_seasons}
#     seasons_labels=NW_seasons.season
#     lat_vals = NW_seasons.lat
#     lon_vals = NW_seasons.lon
#     seasonal = []
#     for i in CTs:
#         seasonal.append(CTs[i])
#     seasonal = np.array(seasonal)
#     seasonal_xr=xr.DataArray(seasonal,
#                   coords = {'CT': list(CTs.keys()),                        
#                             'season': seasons_labels,
#                            'lat': lat_vals,
#                            'lon': lon_vals},
#                   dims = ['CT', 'season', 'lat', 'lon'],
#                   attrs=dict(
#                         description="Seasonal relative frequencies period " + str(year_init)+'-'+str(year_end),
#                         units="%",
#                   ) )

#     seasonal_xr.name = 'rel_freq'
#     return(seasonal_xr)



