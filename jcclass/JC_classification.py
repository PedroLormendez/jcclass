#!/usr/bin/env python
# coding: utf-8

# In[ ]:
"""
@Author: Pedro Herrera-Lormendez
"""

import gc
import numpy as np
import pandas as pd
import xarray as xr
#Importing the directory where the neccesary functions are located
from jcclass import JC_functions #Functions that help compute the CTs

def JC_classification(filename):
    
    '''
    
    @authors: Herrera-Lormendez, Pedro & John, Amal
    TU Bergakademie Freiberg and CNRS/Météo-France
    
    This computes the gridded Jenkinson-Collison circulation types
    derived from the original Lamb Weather Types Classification
    
    Computation of circulation types employs Mean Sea Level Pressure data
    
    :param filename: str. name and directory of the MSLP file
    :return: DataArray of grided circulation types data as an xarray file
    '''
    if type(filename) == str:
        print('Reading filename: ', filename)
        #Reading the file
        DS = xr.open_dataset(filename)
        mslp = JC_functions.renaming_coords(DS)
        #If apply, extracting metadata from Global Models
        is_gcm = False
        try: 
            institution_id = DS.institution_id
            experiment_id  = DS.experiment_id
            source_id      = DS.source_id
            is_gcm         = True
        except:
            pass            
        DS.close()
        del DS
        gc.collect()
          
        mslp_dim_1 = mslp.dims[1]
        #Checking longitude coordinates to be - 180 to 180
        print('Checking if longitude coordinates are -180 to 180...')
        mslp = JC_functions.checking_lon_coords(mslp)
        print('Checking latitude coordinates values...')
        mslp = JC_functions.checking_lat_coords(mslp)

        #Computing factors based on grid size
        dif_lon = float((mslp.lon[1]-mslp.lon[0]))
        dif_lat = float((mslp.lat[1]-mslp.lat[0]))

        factor_lat = float(np.abs(1/dif_lat))
        factor_lon = float(np.abs(1/dif_lon))
        f_lat1 = int(10*factor_lat)
        f_lat2 = int(-10*factor_lat)
        
        f_lon1 = int(15*factor_lon)
        f_lon2 = int(-15*factor_lon)
        #Checking if the MSLP data covers the whole world
        answer_globe = JC_functions.is_world(mslp)
        if answer_globe == True:
            psl_area=mslp[:,f_lat1:f_lat2, :] 
        elif answer_globe == False:
            psl_area=mslp[:,f_lat1:f_lat2, f_lon1:f_lon2]
            
        lat = psl_area.lat
        lon = psl_area.lon
        time = psl_area.time.values
        del psl_area
        gc.collect()
        time_len = len(time)
        lon_list = list(lon)
        lat_list = list(lat)
        len_lon = len(lon_list)
        len_lat = len(lat_list)
        ds = []

        print('Calculating constants') 

        lat_central = lat
        phi = lat_central            
        constants = JC_functions.constants(phi, lon)
        sc = constants[0]
        zwa = constants[1]
        zwb = constants[2]
        zsc = constants[3]            


        print('Checking time formats')

        #Checking the time coordinate values 
        if type(time[0]) == np.datetime64:
            time_pd = pd.to_datetime(time)
            dates = [pd.to_datetime(str(time_pd[t].year) + '-' + str(time_pd[t].month) + '-' + str(time_pd[t].day), 
                                        format = '%Y%m%d',errors = 'ignore') for t in range(len(time))]
        else:
            dates = [pd.to_datetime(str(time[t].year) + '-' + str(time[t].month) + '-' + str(time[t].day), 
                                format = '%Y%m%d',errors = 'ignore') for t in range(len(time))]

        #Extracting the 16-gridded values of MSLP
        #extraction based on point 8 on original map
        print('Extracting the 16 MSLP gridpoints')
        if answer_globe == True:
            gridpoints = JC_functions.extracting_gridpoints_globe(mslp, lat, lon)
            p1  = gridpoints[0]
            p2  = gridpoints[1]
            p3  = gridpoints[2]
            p4  = gridpoints[3]
            p5  = gridpoints[4]
            p6  = gridpoints[5]
            p7  = gridpoints[6]
            p8  = gridpoints[7]
            p9  = gridpoints[8]
            p10 = gridpoints[9]
            p11 = gridpoints[10]
            p12 = gridpoints[11]
            p13 = gridpoints[12]
            p14 = gridpoints[13]
            p15 = gridpoints[14]
            p16 = gridpoints[15]
        elif answer_globe == False:
            gridpoints = JC_functions.extracting_gridpoints_area(mslp, lat, lon)
            p1  = gridpoints[0]
            p2  = gridpoints[1]
            p3  = gridpoints[2]
            p4  = gridpoints[3]
            p5  = gridpoints[4]
            p6  = gridpoints[5]
            p7  = gridpoints[6]
            p8  = gridpoints[7]
            p9  = gridpoints[8]
            p10 = gridpoints[9]
            p11 = gridpoints[10]
            p12 = gridpoints[11]
            p13 = gridpoints[12]
            p14 = gridpoints[13]
            p15 = gridpoints[14]
            p16 = gridpoints[15]
       
        print('Computing flow terms')
        #Computing equations of flows and vorticity                        
        flows = JC_functions.flows(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, sc, zwa, zsc, zwb, lat, lon, time, mslp)
        del (mslp, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, sc, zwa, zsc, zwb)
        gc.collect()
        W  = flows[0] #Westerly flow
        S  = flows[1] #Southerly flow
        F  = flows[2] #Resultant flow
        ZW = flows[3] #Westerly shear vorticity
        ZS = flows[4] #Southerly shear vorticity
        Z  = flows[5] #Total shear vorticity

        del flows
        gc.collect()            

        print('Computing flow directions')
        #Computing the wind direction values          
        dd = np.arctan(W/S)
        deg = np.rad2deg(dd)
        deg=np.mod(180+np.rad2deg(np.arctan2(W, S)),360) 

        del (W, S, ZW, ZS)
        gc.collect()        
        #https://confluence.ecmwf.int/pages/viewpage.action?pageId=133262398 
        #Assigning the Wind Direction labels
        direction = JC_functions.direction_def_NH(deg)
        direction = xr.where(deg.lat < 0, JC_functions.direction_def_SH(deg), direction)            

        print('Determining the Circulation types')
        #Determination of Circulation Type (27 Original types)
        lwt = JC_functions.assign_lwt(F, Z, direction)

        del (F, Z, direction)
        gc.collect()
        
        #Storing the gridded Circulation Types in an xarray file
        print('Saving the data in an xarray format')
        if (mslp_dim_1 == 'latitude') or (mslp_dim_1 == 'lat'):
            output=xr.DataArray(data = lwt.values,
                coords = {'time': time,
                        'lat': lat_list, 
                        'lon': lon_list},
                        dims = ['time', 'lat', 'lon'])
            output.name = 'CT' #Assigning variable name
        elif mslp_dim_1 == 'number':
            output=xr.DataArray(data = lwt.values,
                coords = {'time': time,
                          'number':mslp.number,
                          'lat': lat_list, 
                          'lon': lon_list},
                        dims = ['time','number', 'lat', 'lon'])
            output.name = 'CT' #Assigning variable name
        if is_gcm == True:
            output.attrs = {
                'description':'Gridded Lamb circulation types derived from MSLP data based on the automated Jenkinson-Collison classification',
                'institution_id': institution_id,
                'source_id': source_id,
                'experiment_id': experiment_id}
        elif is_gcm== False:
            output.attrs = {
                'description':'Gridded Lamb circulation types derived from MSLP data based on the automated Jenkinson-Collison classification'}
        output = JC_functions.checking_lat_coords(output)
       
        print('The End!')


    else:
        raise TypeError("Incorrect filename directory. Only strings allowed")
    
    return output