#!/usr/bin/env python
# coding: utf-8

# In[ ]:
"""
@Author: Pedro Herrera-Lormendez
"""
#Importing neccesary modules
import gc
import numpy as np
import pandas as pd
import xarray as xr

def renaming_coords(DS):
    """
    This function reads and extracts the latitude and loongitude coordinate
    names as well as the name of the variable for MSLP. 
    Then read the variable and divides by 100 to convert to hPa
    If MSLP variable is different to 'msl' or 'psl', the user
    can input the name of the variable manually
    :param DS: Xarray dataset of MSLP.
    :return mslp: DataArray of MSLP data with lat,lon coordinates
    """
#Extracting name of longitude
    for lon_name in ('longitude', 'lon'):
        try:
            DS[lon_name]
            lon_name = lon_name
            break
        except KeyError:
            continue
    else:
        err_msg = (
                'Coodinate name for longitude different to "lon" or "longitude" '
            )
        raise KeyError(err_msg)
    #Extracting name of latitude    
    for lat_name in ('latitude', 'lat'):
        try:
            DS[lat_name]
            lat_name = lat_name
            break
        except KeyError:
            continue
    else:
        err_msg = (
                'Coodinate name for latitude different to "lat" or "latitude" '
            )
        raise KeyError(err_msg)

    #Renaming latitude, longitude coordinates to 'lat' and 'lon'
    if lat_name == 'latitude':
        DS = DS.rename({lat_name:'lat'})
    elif lat_name == 'lat':
        pass
    if lon_name == 'longitude':
        DS = DS.rename({lon_name:'lon'})
    elif lon_name == 'lon':
        pass
    #Reading variable
    for var_name in ('msl','psl'): #Usual names for MSLP variables
        try:
            mslp = DS[var_name]
            mslp /= 100
            break
        except KeyError:
            continue
    else: #If variable has a name different to 'msl' or 'psl'
        print('File contains a variable name different to "msl" or "psl".\n'
            'Please pvovide the variable name of the xr.Dataset containing '
            'sea level pressure:')
        var_name = input()
        mslp = DS[str(var_name)]
        mslp /= 100
    return(mslp)    

def checking_lat_coords(data):
    """
    This function checks and fixes the latitude coordinate
    values to go in incremental values (e.g., -80 to 80ºN)

    :param mslp: mean sea level pressure data in DataArray format
    """
    if data.lat[0] > data.lat[-1]:
        data = data.reindex(lat = list(reversed(data.lat)))
    else:
        pass
    return(data)

def checking_lon_coords(data):
    """
    This function checks and fixes the longitude coordinate
    values going from 180 to -180 º.
    
    :param mslp: mean sea level pressure data in DataArray format
    """
    lon_name = 'lon'
    if data[lon_name][-1] > 180:
        # Adjust lon values to make sure they are within (-180, 180)
        data['_longitude_adjusted'] = xr.where(
            data[lon_name] > 180,
            data[lon_name] - 360,
            data[lon_name])

        # reassign the new coords to as the main lon coords
        # and sort DataArray using new coordinate values
        data = (
            data
            .swap_dims({lon_name: '_longitude_adjusted'})
            .sel(**{'_longitude_adjusted': sorted(data._longitude_adjusted)})
            .drop(lon_name))

        data = data.rename({'_longitude_adjusted': lon_name})
    else:
        pass
    return(data)
def is_world(data):
    dif_lon = np.abs(data.lon[0] - data.lon[1])
    dif_lat = np.abs(data.lat[0] - data.lat[1])
    condition_east  = data.lon[-1]>= (180 - dif_lon) #East
    condition_west  = data.lon[0]<= (-180 + dif_lon) #West
    es_mundo = False
    if condition_west == condition_east:
        es_mundo = True
    else:
        pass
    return(es_mundo)


def constants(phi, lon):
    """
    Computing values of constants dependant on latitude and longitude
    They represent the constants referred to the relative differences
    between the grid-point spacing in the E-W and N-S direction
    
    :param phi: values of central latitude gridpoints
    :param lon: longitude values
    """
    SC = 1/np.cos(np.deg2rad(phi))
    SC.name="longitue"
    sc=xr.concat([SC]*len(lon),'logitude').T

    ZWA = np.sin(np.deg2rad(phi)) / np.sin (np.deg2rad(phi - 5))
    ZWA.name="longitue"
    zwa=xr.concat([ZWA]*len(lon),'logitude').T

    ZWB = np.sin(np.deg2rad(phi)) / np.sin (np.deg2rad(phi + 5))
    ZWB.name="longitue"
    zwb=xr.concat([ZWB]*len(lon),'logitude').T

    ZSC = (1/(2*(np.cos(np.deg2rad(phi))**2)))
    ZSC.name="longitue"
    zsc=xr.concat([ZSC]*len(lon),'logitude').T
    return (sc, zwa, zwb, zsc)

def direction_def_NH(deg_used):
    '''
    This function assigns the wind direction labels of the circulation types for 
    the Northern Hemisphere
    
    :param deg_used: xarray of wind direction values in degrees

    '''
    direction = xr.where( (deg_used>247) & (deg_used<=292), 'W', np.nan)
    direction = xr.where( (deg_used>292) & (deg_used<=337), 'NW', direction)
    direction = xr.where( (deg_used>337), 'N', direction)
    direction = xr.where( (deg_used>=0) & (deg_used<=22), 'N', direction)
    direction = xr.where( (deg_used>22) & (deg_used<=67), 'NE', direction)
    direction = xr.where( (deg_used>67) & (deg_used<=112), 'E', direction)
    direction = xr.where( (deg_used>112) & (deg_used<=157), 'SE', direction)
    direction = xr.where( (deg_used>157) & (deg_used<=202), 'S', direction)
    direction = xr.where( (deg_used>202) & (deg_used<=247), 'SW', direction)
    return(direction)

def direction_def_SH(deg_used):
    '''
    This function assigns the wind direction labels of the circulation types for 
    the Southern Hemisphere
    
    :param deg_used: xarray of wind direction values in degrees
    '''    
    direction = xr.where( (deg_used>247) & (deg_used<=292), 'E', np.nan)
    direction = xr.where( (deg_used>292) & (deg_used<=337), 'SE', direction)
    direction = xr.where( (deg_used>337), 'S', direction)
    direction = xr.where( (deg_used>=0) & (deg_used<=22), 'S', direction)
    direction = xr.where( (deg_used>22) & (deg_used<=67), 'SW', direction)
    direction = xr.where( (deg_used>67) & (deg_used<=112), 'W', direction)
    direction = xr.where( (deg_used>112) & (deg_used<=157), 'NW', direction)
    direction = xr.where( (deg_used>157) & (deg_used<=202), 'N', direction)
    direction = xr.where( (deg_used>202) & (deg_used<=247), 'NE', direction)
    return(direction)

def assign_lwt(F_i, Z_i, direction_i):
    '''
    This function assigns the corresponding circulation types' coding
    
    :param         F_i: xarray of Total Flow term (F)
    :param         Z_i: xarry of Total Shear Vorticity term (Z)
    :param direction_i: xarray of Flow Direction
    '''

    ### Hybrid Anticyclonic flows ###
    lwt = xr.where( (Z_i<0) & (direction_i=='NE'), 1, np.nan)    
    lwt = xr.where( (Z_i<0) & (direction_i=='E'),  2, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='SE'), 3, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='S'),  4, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='SW'), 5, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='W'),  6, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='NW'), 7, lwt)
    lwt = xr.where( (Z_i<0) & (direction_i=='N'),  8, lwt)
    ### Hybrid Cyclonic flows ###
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='NE'), 11, lwt)    
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='E'),  12, lwt)
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='SE'), 13, lwt)
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='S'),  14, lwt)
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='SW'), 15, lwt)
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='W'),  16, lwt)
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='NW'), 17, lwt)
    lwt = xr.where( (np.absolute(Z_i)<F_i) & (direction_i=='N'),  18, lwt)
    ### Purely Cyclonic ###
    lwt = xr.where( ( (np.absolute(Z_i)) > (2*F_i) ) & (Z_i>0), 20, lwt)
    ### Purely Anticyclonic ###
    lwt = xr.where( ( (np.absolute(Z_i)) > (2*F_i) ) & (Z_i<0),  0, lwt)
    ### Directional flows ###
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='NE'), 21, lwt)    
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='E'),  22, lwt)
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='SE'), 23, lwt)
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='S'),  24, lwt)
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='SW'), 25, lwt)
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='W'),  26, lwt)
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='NW'), 27, lwt)
    lwt = xr.where( (np.absolute(Z_i)>F_i) & (np.absolute(Z_i) < 2*F_i) & (Z_i>0) & (direction_i=='N'),  28, lwt)
    ### Low Flow / Unclassified / Weak Flow ###
    lwt = xr.where( (F_i<6) & (np.absolute(Z_i) < 6), -1, lwt)

    return lwt
    
def extracting_gridpoints_area(mslp, lat, lon):
    """
    This function extracts the 16 moving gridded points over a defined area (not globe)
    given a Reanalysis or Global Climate Model Dataset. This gridpoints are
    neccesary for the computation of the terms
    """
    #Gridpoint 1
    lat1 = lat+10
    lon1 = lon-5
    lat1 = lat.sel(lat = lat1, method = 'nearest')        
    lon1 = lon.sel(lon = lon1, method = 'nearest')     
    p1 = np.array(mslp.sel(lat = lat1, lon = lon1))
    del(lat1, lon1)
    gc.collect()
    #Gridpoint 2
    lat2 = lat + 10
    lon2 = lon + 5
    lat2 = lat.sel(lat = lat2, method = 'nearest')        
    lon2 = lon.sel(lon = lon2, method = 'nearest')    
    p2 = np.array(mslp.sel(lat = lat2, lon = lon2))
    del (lat2, lon2)
    gc.collect()
    #Gridpoint 3
    lat3 = lat + 5
    lon3 = lon - 15
    lat3 = lat.sel(lat = lat3, method = 'nearest')        
    lon3 = lon.sel(lon = lon3, method = 'nearest')    
    p3 = np.array(mslp.sel(lat = lat3, lon = lon3))
    del (lat3, lon3)
    gc.collect()
    #Gridpoint 4
    lat4 = lat + 5
    lon4 = lon  -5
    lat4 = lat.sel(lat = lat4, method = 'nearest')        
    lon4 = lon.sel(lon = lon4, method = 'nearest')    
    p4 = np.array(mslp.sel(lat = lat4, lon = lon4))
    del (lat4, lon4)
    gc.collect()
    #Gridpoint 5
    lat5 = lat + 5
    lon5 = lon + 5
    lat5 = lat.sel(lat = lat5, method = 'nearest')        
    lon5 = lon.sel(lon = lon5, method = 'nearest')    
    p5 = np.array(mslp.sel(lat = lat5, lon = lon5))
    del (lat5, lon5)
    gc.collect()
    #Gridpoint 6
    lat6 = lat + 5
    lon6 = lon + 15
    lat6 = lat.sel(lat = lat6, method = 'nearest')        
    lon6 = lon.sel(lon = lon6, method = 'nearest')    
    p6 = np.array(mslp.sel(lat = lat6, lon = lon6))
    del (lat6, lon6)
    gc.collect()
    #Gridpoint 7
    lat7 = lat
    lon7 = lon - 15
    lat7 = lat.sel(lat = lat7, method = 'nearest')        
    lon7 = lon.sel(lon = lon7, method = 'nearest')    
    p7 = np.array(mslp.sel(lat = lat7, lon = lon7))
    del (lat7, lon7)
    gc.collect()
    #Gridpoint 8
    lat8 = lat
    lon8 = lon -5
    lat8 = lat.sel(lat = lat8, method = 'nearest')        
    lon8 = lon.sel(lon = lon8, method = 'nearest')    
    p8 = np.array(mslp.sel(lat = lat8, lon = lon8))
    del (lat8, lon8)
    gc.collect()
    #Gridpoint 9
    lat9 = lat
    lon9 = lon + 5
    lat9 = lat.sel(lat = lat9, method = 'nearest')        
    lon9 = lon.sel(lon = lon9, method = 'nearest')    
    p9 = np.array(mslp.sel(lat = lat9, lon = lon9))
    del (lat9, lon9)
    gc.collect()
    #Gridpoint 10
    lat10 = lat
    lon10 = lon + 15
    lat10 = lat.sel(lat = lat10, method = 'nearest')        
    lon10 = lon.sel(lon = lon10, method = 'nearest')    
    p10 = np.array(mslp.sel(lat = lat10, lon = lon10))
    del (lat10, lon10)
    gc.collect()
    #Gridpoint 11
    lat11 = lat - 5
    lon11 = lon - 15
    lat11 = lat.sel(lat = lat11, method = 'nearest')        
    lon11 = lon.sel(lon = lon11, method = 'nearest')    
    p11 = np.array(mslp.sel(lat = lat11, lon = lon11))
    del (lat11, lon11)
    gc.collect()
    #Gridpoint 12
    lat12 = lat - 5
    lon12 = lon - 5
    lat12 = lat.sel(lat = lat12, method = 'nearest')        
    lon12 = lon.sel(lon = lon12, method = 'nearest')    
    p12 = np.array(mslp.sel(lat = lat12, lon = lon12))
    del (lat12, lon12)
    gc.collect()
    #Gridpoint 13
    lat13 = lat - 5
    lon13 = lon + 5
    lat13 = lat.sel(lat = lat13, method = 'nearest')        
    lon13 = lon.sel(lon = lon13, method = 'nearest')    
    p13 = np.array(mslp.sel(lat = lat13, lon = lon13))
    del (lat13, lon13)
    gc.collect()
    #Gridpoint 14
    lat14 = lat - 5
    lon14 = lon + 15
    lat14 = lat.sel(lat = lat14, method = 'nearest')        
    lon14 = lon.sel(lon = lon14, method = 'nearest')    
    p14 = np.array(mslp.sel(lat = lat14, lon = lon14))
    del (lat14, lon14)
    gc.collect()
    #Gridpoint 15
    lat15 = lat - 10
    lon15 = lon - 5
    lat15 = lat.sel(lat = lat15, method = 'nearest')        
    lon15 = lon.sel(lon = lon15, method = 'nearest')    
    p15 = np.array(mslp.sel(lat = lat15, lon = lon15))
    del (lat15, lon15)
    gc.collect()
    #Gridpoint 16
    lat16 = lat - 10
    lon16 = lon + 5
    lat16 = lat.sel(lat = lat16, method = 'nearest')        
    lon16 = lon.sel(lon = lon16, method = 'nearest')    
    p16 = np.array(mslp.sel(lat = lat16, lon = lon16))
    del (lat16, lon16)
    gc.collect()
    return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16)
    
def extracting_gridpoints_globe(mslp, lat, lon):
    """
    This function extracts the 16 moving gridded points over the whole globe
    given a Reanalysis or Global Climate Model dataset. These gridpoints are
    neccesary for the computation fo the terms
    """
    #Gridpoint 1
    lat1 = lat + 10
    lon1 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat1 = lat.sel(lat = lat1, method = 'nearest')        
    lon1 = lon.sel(lon = lon1, method = 'nearest')    
    p1 = np.array(mslp.sel(lat = lat1, lon = lon1))
    del (lat1, lon1)
    gc.collect()

    #Gridpoint 2
    lat2 = lat + 10
    lon2 = xr.where(lon>175, lon+5-360, lon+5)
    lon2 = xr.where(lon2 == 180, -180, lon2)
    lat2 = lat.sel(lat = lat2, method = 'nearest')        
    lon2 = lon.sel(lon = lon2, method = 'nearest')    
    p2 = np.array(mslp.sel(lat = lat2, lon = lon2))
    del (lat2, lon2)
    gc.collect()

    #Gridpoint 3
    lat3 = lat + 5
    lon3 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat3 = lat.sel(lat = lat3, method = 'nearest')        
    lon3 = lon.sel(lon = lon3, method = 'nearest')    
    p3 = np.array(mslp.sel(lat = lat3, lon = lon3))
    del (lat3, lon3)
    gc.collect()    

    #Gridpoint 4
    lat4 = lat + 5
    lon4 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat4 = lat.sel(lat = lat4, method = 'nearest')        
    lon4 = lon.sel(lon = lon4, method = 'nearest')    
    p4 = np.array(mslp.sel(lat = lat4, lon = lon4))
    del (lat4, lon4)
    gc.collect()    

    #Gridpoint 5
    lat5 = lat + 5
    lon5 = xr.where(lon>175, lon+5-360, lon+5)
    lon5 = xr.where(lon5 == 180, -180, lon5)
    lat5 = lat.sel(lat = lat5, method = 'nearest')        
    lon5 = lon.sel(lon = lon5, method = 'nearest')    
    p5 = np.array(mslp.sel(lat = lat5, lon = lon5))
    del (lat5, lon5)
    gc.collect()    

    #Gridpoint 6
    lat6 = lat + 5
    lon6 = xr.where(lon>165, lon+15-360,lon+15)
    lon6 = xr.where(lon6 == 180, -180, lon6)
    lat6 = lat.sel(lat = lat6, method = 'nearest')        
    lon6 = lon.sel(lon = lon6, method = 'nearest')    
    p6 = np.array(mslp.sel(lat = lat6, lon = lon6))
    del (lat6, lon6)
    gc.collect()    

    #Gridpoint 7
    lat7 = lat
    lon7 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat7 = lat.sel(lat = lat7, method = 'nearest')        
    lon7 = lon.sel(lon = lon7, method = 'nearest')    
    p7 = np.array(mslp.sel(lat = lat7, lon = lon7))
    del (lat7, lon7)
    gc.collect()    

    #Gridpoint 8
    lat8 = lat
    lon8 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat8 = lat.sel(lat = lat8, method = 'nearest')        
    lon8 = lon.sel(lon = lon8, method = 'nearest')    
    p8 = np.array(mslp.sel(lat = lat8, lon = lon8))
    del (lat8, lon8)
    gc.collect()    

    #Gridpoint 9
    lat9 = lat
    lon9 = xr.where(lon>175, lon+5-360, lon+5)
    lon9 = xr.where(lon9 == 180, -180, lon9)
    lat9 = lat.sel(lat = lat9, method = 'nearest')        
    lon9 = lon.sel(lon = lon9, method = 'nearest')    
    p9 = np.array(mslp.sel(lat = lat9, lon = lon9))
    del (lat9, lon9)
    gc.collect()    

    #Gridpoint 10
    lat10 = lat
    lon10 = xr.where(lon>165, lon+15-360, lon+15)
    lon10 = xr.where(lon10 == 180, -180, lon10)
    lat10 = lat.sel(lat = lat10, method = 'nearest')        
    lon10 = lon.sel(lon = lon10, method = 'nearest')    
    p10 = np.array(mslp.sel(lat = lat10, lon = lon10))
    del (lat10, lon10)
    gc.collect()    

    #Gridpoint 11
    lat11 = lat - 5
    lon11 = xr.where(lon<-165, 360+lon-15, lon-15)
    lat11 = lat.sel(lat = lat11, method = 'nearest')        
    lon11 = lon.sel(lon = lon11, method = 'nearest')    
    p11 = np.array(mslp.sel(lat = lat11, lon = lon11))
    del (lat11, lon11)
    gc.collect()        

    #Gridpoint 12
    lat12 = lat - 5
    lon12 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat12 = lat.sel(lat = lat12, method = 'nearest')        
    lon12 = lon.sel(lon = lon12, method = 'nearest')    
    p12 = np.array(mslp.sel(lat = lat12, lon = lon12))
    del (lat12, lon12)
    gc.collect()        

    #Gridpoint 13
    lat13 = lat - 5 
    lon13 = xr.where(lon>175, lon+5-360, lon+5)
    lon13 = xr.where(lon13 == 180, -180, lon13)
    lat13 = lat.sel(lat = lat13, method = 'nearest')        
    lon13 = lon.sel(lon = lon13, method = 'nearest')    
    p13 = np.array(mslp.sel(lat = lat13, lon = lon13))
    del (lat13, lon13)
    gc.collect()        

    #Gridpoint 14
    lat14 = lat - 5
    lon14 = xr.where(lon>165, lon+15-360, lon+15)
    lon14 = xr.where(lon14 == 180, -180, lon14)
    lat14 = lat.sel(lat = lat14, method = 'nearest')        
    lon14 = lon.sel(lon = lon14, method = 'nearest')    
    p14 = np.array(mslp.sel(lat = lat14, lon = lon14))
    del (lat14, lon14)
    gc.collect()        

    #Gridpoint 15
    lat15 = lat - 10
    lon15 = xr.where(lon<-175, 360+lon-5, lon-5)
    lat15 = lat.sel(lat = lat15, method = 'nearest')        
    lon15 = lon.sel(lon = lon15, method = 'nearest')    
    p15 = np.array(mslp.sel(lat = lat15, lon = lon15))
    del (lat15, lon15)
    gc.collect()        

    #Gridpoint 16
    lat16 = lat - 10
    lon16 = xr.where(lon>175, lon+5-360, lon+5)
    lon16 = xr.where(lon16 == 180, -180, lon16)
    lat16 = lat.sel(lat = lat16, method = 'nearest')        
    lon16 = lon.sel(lon = lon16, method = 'nearest')    
    p16 = np.array(mslp.sel(lat = lat16, lon = lon16))
    del (lat16, lon16)
    gc.collect()        
    
    return (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16)

def flows(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, sc, zwa, zsc, zwb, lat, lon, time, mslp):
    """
    This function computes the indices associated with the direction and vorticity
    of geostrophic flow given a reanalyses or GCM dataset
    More info: Jones, P. D., Hulme, M., & Briffa, K. R. (1993). 
    A comparison of Lamb circulation types with an objective classification scheme.  
    International Journal of Climatology(6), 655–663. https://doi.org/10.1002/joc.3370130606
    
    The function employs as parameters: 
    - the 16 gridded points of MSLP (p1 to p16)
    - The latitude dependant constants (sc, zwa, zsc  and zwb)
    - latitude, longitude, time and MSLP data
    
    This function also makes it possible to work with a dataset with an extra
    dimension named "number" which reffers to the number of a set of an ensemble. 
    This can be used for subseasonal forecasts coming from 
    the Climate Data Store: https://cds.climate.copernicus.eu/cdsapp#!/home
    """
    #Westerly Flow
    W = ((0.5)*( p12 + p13 )) - ((0.5)*( p4 + p5 ))
    if mslp.dims[1] == 'lat':
        W = xr.DataArray(W, 
                          coords = {'time': time, 'lat':lat, 'lon':lon}, 
                          dims = ['time', 'lat', 'lon'])
    elif mslp.dims[1] == 'number':
        W = xr.DataArray(W, 
                          coords = {'time': time, 'number':mslp.number ,'lat':lat, 'lon':lon}, 
                          dims = ['time','number' ,'lat', 'lon'])
        
    #Southerly Flow
    S = np.array(sc)*(((0.25)*(p5 + (2 * p9) + p13)) - ((0.25)*(p4 + (2 * p8) + p12)))
    if mslp.dims[1] == 'lat':
        S = xr.DataArray(S, 
                          coords = {'time': time, 'lat':lat, 'lon':lon}, 
                          dims = ['time', 'lat', 'lon'])
    elif mslp.dims[1] == 'number':
        S = xr.DataArray(S, 
                          coords = {'time': time, 'number':mslp.number ,'lat':lat, 'lon':lon}, 
                          dims = ['time','number', 'lat', 'lon'])        
    #Resultant Flow 
    F = np.sqrt(S**2 + W**2)
    #Westerly Shear Vorticity
    ZW = (np.array(zwa)*( (0.5)*(p15 + p16) - (0.5)*(p8 + p9))) - (np.array(zwb)*((0.5)*(p8 + p9) - (0.5)*(p1 + p2)))
    if mslp.dims[1] == 'lat':
        ZW = xr.DataArray(ZW, 
                          coords = {'time': time, 'lat':lat, 'lon':lon}, 
                          dims = ['time', 'lat', 'lon'])
    elif mslp.dims[1] == 'number':
        ZW = xr.DataArray(ZW, 
                              coords = {'time': time, 'number':mslp.number ,'lat':lat, 'lon':lon}, 
                              dims = ['time', 'number', 'lat', 'lon'])        
    #Southerly Shear Vorticity
    ZS = np.array(zsc) * ( ((0.25)*(p6 + (2 * p10) + p14)) - ((0.25)*(p5 + (2 * p9) + p13)) -((0.25)*(p4 + (2 * p8) + p12)) +((0.25)*(p3 + (2 * p7) + p11)) )
    #Total Shear Vorticity
    if mslp.dims[1] == 'lat':    
        ZS = xr.DataArray(ZS, 
                          coords = {'time': time, 'lat':lat, 'lon':lon}, 
                          dims = ['time', 'lat', 'lon'])
    elif mslp.dims[1] == 'number':
        ZS = xr.DataArray(ZS, 
                          coords = {'time': time,'number':mslp.number ,'lat':lat, 'lon':lon}, 
                          dims = ['time', 'number', 'lat', 'lon'])
        
    Z = ZW + ZS
    return(W, S, F, ZW, ZS, Z)
