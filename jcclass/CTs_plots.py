#!/usr/bin/env python
# coding: utf-8

# In[1]:
"""
@Author: Pedro Herrera-Lormendez
"""

import numpy as np
import pandas as pd
import xarray as xr
#from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import cftime
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib.colors as colors
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker

from jcclass import JC_functions
from jcclass import CTs_functions

def plot_CT(CT, lat_south=-80, lat_north=80, lon_west=-180, lon_east=180):
    '''
    This function plots the 11 circulation types to a map
    
    :param CT: A 2D ['lat','lon'] DataArray file of the 27 circulation types
    *args
    :param lat_south: int -80 to 80
    :param lat_north: int -80 to 80
    :param lon_west : int -180 to 180
    :param lon_east : int -180 to 180
    '''
    lat_north = CT.lat.sel(lat = lat_north, method = 'nearest')
    lat_south = CT.lat.sel(lat = lat_south, method = 'nearest')
    lon_west = CT.lon.sel(lon = lon_west, method = 'nearest')
    lon_east = CT.lon.sel(lon = lon_east, method = 'nearest')
    CT = CT.sel(lat = slice(lat_south, lat_north), lon = slice(lon_west, lon_east))        
    dif_x = lon_east - (lon_west)
    dif_y = lat_north - (lat_south)
    size_x = 12
    size_y = 10
    if dif_x > dif_y:
        size_x = 12
        size_y = size_x * (dif_y / dif_x)
    elif dif_x < dif_y:
        size_y = 12
        size_x = size_y * (dif_y / dif_x)
    
    CT = xr.where((CT.lat < 10) & (CT.lat > -10), np.nan, CT)
    highs = xr.where( (CT>=1) & (CT<=8), 1, np.nan)
    lows = xr.where( (CT>=21) & (CT<=28), 1, np.nan)
    CT = CTs_functions.eleven_CTs(CT)    
    #Defining colours to plot CTs
    colores = ListedColormap(["#7C7C77", "#17344F", "#0255F4","#0F78ED", "#9E09EE", "#F6664C",
                         "#F24E64", "#D3C42D", "#2FC698", 
                         "#20E1D7", "#BD0000"])  #C, N, NW, W, SW, S, SE, E, NE, A, LF  
    bounds = np.arange(-1,11,1)
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=12)
    lons, lats = CT.lon, CT.lat
    #Defining size and map boundaries    
    plt.gcf().clear()   
    fig= plt.figure(figsize = (size_x,size_y))
    proj = ccrs.PlateCarree()
    ax = plt.axes(projection=proj)
    ax.set_extent([lon_west, lon_east, lat_south, lat_north], proj)
    im = plt.pcolor(lons, lats, CT,
                 transform=proj, norm = norm, cmap = colores)
    ima = plt.contourf(lons, lats, highs, colors = None, hatches = ['....'], alpha = 0)
    imc = plt.contourf(lons, lats, lows, colors = None, hatches = ['----'], alpha = 0)

    ax.coastlines('50m')
    ax.stock_img()

    gl = ax.gridlines(crs=proj)
    gl.xlabels_top = False
    gl.xlabels_bottom = True
    gl.ylabels_left = True
    gl.ylabels_right = False
    gl.xlines = False
    gl.ylines = False
    gl.ylocator = mticker.FixedLocator([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    gl.xlocator = mticker.FixedLocator([-180,-120,-60, 0, 60, 120, 180])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
   
    #Legends
    ax = plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])
    legend_elements = [  Line2D([0], [0],marker ='o', color = '#7C7C77',markerfacecolor = None,linestyle='None', markersize = 17,label='LF'),
                         Line2D([0], [0], marker='o', color='#17344F', markerfacecolor=None, linestyle='None', markersize=17, label='A'),
                         Line2D([0], [0], marker='o', color='#0255F4', markerfacecolor=None, linestyle='None', markersize=17, label='NE'),
                         Line2D([0], [0], marker='o', color='#0F78ED', markerfacecolor=None, linestyle='None', markersize=17, label='E'),
                         Line2D([0], [0], marker='o', color='#9E09EE', markerfacecolor=None, linestyle='None', markersize=17, label='SE'),
                         Line2D([0], [0], marker='o', color='#F6664C', markerfacecolor=None, linestyle='None', markersize=17, label='S'),
                         Line2D([0], [0], marker='o', color='#F24E64', markerfacecolor=None, linestyle='None', markersize=17, label='SW'),
                         Line2D([0], [0], marker='o', color='#D3C42D', markerfacecolor=None, linestyle='None', markersize=17, label='W'),
                         Line2D([0], [0], marker='o', color='#2FC698', markerfacecolor=None, linestyle='None', markersize=17, label='NW'),
                         Line2D([0], [0], marker='o', color='#20E1D7', markerfacecolor=None, linestyle='None', markersize=17, label='N'),
                         Line2D([0], [0], marker='o', color='#BD0000', markerfacecolor=None, linestyle='None', markersize=17, label='C'),
                         Line2D([0], [0], marker=None, color ='#000000',markerfacecolor=None, linestyle='--', markersize=17, label='Partly Cyclonic'),
                         Line2D([0], [0], marker=None, color ='#000000',markerfacecolor=None, linestyle='dotted', markersize=17, label='Partly Anticylonic'),                       
                      ]

    ax.legend(handles=legend_elements,loc = 'center', bbox_to_anchor=(1.15, 0.50),frameon = False, prop={'size': 14}) #X,Y, LENGTH, WIDHT
    
    plt.title(str(CT.time.values), size = 16)
    plt.tight_layout()
    plt.ioff()
    return fig

def plot_CT_MSLP(CT, MSLP, lat_south=-80, lat_north=80, lon_west=-180, lon_east=180):
    '''
    This function plots the 11 circulation types to a map
    ¡! Works only with Basemap module
    
    :param CT: xarray file of the 27 circulation types
    :param MSLP: a 2D ['lat', 'lon'] DataArray of Mean Sea Level Pressure data in Pa
    *args
    :param lat_south: int -80 to 80
    :param lat_north: int -80 to 80
    :param lon_west : int -180 to 180
    :param lon_east : int -180 to 180
    '''
    MSLP = JC_functions.renaming_coords(MSLP)


    MSLP = JC_functions.checking_lon_coords(MSLP)
    MSLP = JC_functions.checking_lat_coords(MSLP)

    lat_north = CT.lat.sel(lat = lat_north, method = 'nearest')
    lat_south = CT.lat.sel(lat = lat_south, method = 'nearest')
    lon_west = CT.lon.sel(lon = lon_west, method = 'nearest')
    lon_east = CT.lon.sel(lon = lon_east, method = 'nearest')
    CT = CT.sel(lat = slice(lat_south, lat_north), lon = slice(lon_west, lon_east))
    dif_x = lon_east - (lon_west)
    dif_y = lat_north - (lat_south)
    size_x = 12
    size_y = 10
    if dif_x > dif_y:
        size_x = 12
        size_y = size_x * (dif_y / dif_x)
    elif dif_x < dif_y:
        size_y = 12
        size_x = size_y * (dif_y / dif_x)        
        
    MSLP = MSLP.sel(lat = slice(lat_south, lat_north), lon = slice(lon_west, lon_east))
    lat = MSLP.lat
    lon = MSLP.lon
    lon_list = list(lon)
    lat_list = list(lat)          
    CT = xr.where((CT.lat < 10) & (CT.lat > -10), np.nan, CT)
    highs = xr.where( (CT>=1) & (CT<=8), 1, np.nan)
    lows = xr.where( (CT>=21) & (CT<=28), 1, np.nan)
    CT = CTs_functions.eleven_CTs(CT)           

    #Defining colours to plot CTs
    colores = ListedColormap(["#7C7C77", "#17344F", "#0255F4","#0F78ED", "#9E09EE", "#F6664C",
                         "#F24E64", "#D3C42D", "#2FC698", 
                         "#20E1D7", "#BD0000"])  #C, N, NW, W, SW, S, SE, E, NE, A, LF  
    bounds = np.arange(-1,11,1)
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=12)
    lons, lats = np.meshgrid(CT.lon, CT.lat)
    #Defining size and map boundaries
    plt.gcf().clear()   
    fig= plt.figure(figsize = (size_x,size_y))
    proj = ccrs.PlateCarree()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_west, lon_east, lat_south, lat_north], proj)
    ax.coastlines('50m')

    ax.stock_img()
    
    im = plt.pcolor(lons, lats, CT,
             transform=proj, norm = norm, cmap = colores, alpha = 0.75)
    from scipy.ndimage.filters import gaussian_filter
    data3 = gaussian_filter(MSLP, sigma=.8)    
    im2 = plt.contour(lons, lats, data3, 
                      np.arange(1012-40, 1012+44, 4),transform=proj, colors = '0.10', linewidths = 0.5)
    ima = plt.contourf(lons, lats, highs, colors = None, hatches = ['....'], alpha = 0)
    imc = plt.contourf(lons, lats, lows, colors = None, hatches = ['----'], alpha = 0)

    plt.clabel(im2, im2.levels, inline=True,fmt ='%.0f', fontsize=10)

    gl = ax.gridlines(crs=proj)
    gl.xlabels_top = False
    gl.xlabels_bottom = True
    gl.ylabels_left = True
    gl.ylabels_right = False
    gl.xlines = False
    gl.ylines = False
    gl.ylocator = mticker.FixedLocator([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    gl.xlocator = mticker.FixedLocator([-180, -150,-120,-90,-60,-30, 0, 30, 60, 90, 120, 150, 180])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    legend_elements = [  Line2D([0], [0],marker ='o', color = '#7C7C77',markerfacecolor = None,linestyle='None', markersize = 17,label='LF'),
                         Line2D([0], [0], marker='o', color='#17344F', markerfacecolor=None, linestyle='None', markersize=17, label='A'),
                         Line2D([0], [0], marker='o', color='#0255F4', markerfacecolor=None, linestyle='None', markersize=17, label='NE'),
                         Line2D([0], [0], marker='o', color='#0F78ED', markerfacecolor=None, linestyle='None', markersize=17, label='E'),
                         Line2D([0], [0], marker='o', color='#9E09EE', markerfacecolor=None, linestyle='None', markersize=17, label='SE'),
                         Line2D([0], [0], marker='o', color='#F6664C', markerfacecolor=None, linestyle='None', markersize=17, label='S'),
                         Line2D([0], [0], marker='o', color='#F24E64', markerfacecolor=None, linestyle='None', markersize=17, label='SW'),
                         Line2D([0], [0], marker='o', color='#D3C42D', markerfacecolor=None, linestyle='None', markersize=17, label='W'),
                         Line2D([0], [0], marker='o', color='#2FC698', markerfacecolor=None, linestyle='None', markersize=17, label='NW'),
                         Line2D([0], [0], marker='o', color='#20E1D7', markerfacecolor=None, linestyle='None', markersize=17, label='N'),
                         Line2D([0], [0], marker='o', color='#BD0000', markerfacecolor=None, linestyle='None', markersize=17, label='C'),
                Line2D([0], [0], marker=None, color ='#000000',markerfacecolor=None, linestyle='--', markersize=17, label='Partly Cyclonic'),
                         Line2D([0], [0], marker=None, color ='#000000',markerfacecolor=None, linestyle='dotted', markersize=17, label='Partly Anticylonic'),                       
                      ]

    ax.legend(handles=legend_elements,loc = 'center', bbox_to_anchor=(1.15, 0.50),frameon = False, prop={'size': 14}) #X,Y, LENGTH, WIDHT                         

    #plt.legend(handles=legend_elements, loc='right', bbox_to_anchor=(0.65, 0.25, 0.5, 0.5),frameon = False, prop={'size': 14}) #X,Y, LENGTH, WIDHT
    plt.title(str(CT.time.values), size = 16, y = 1.05)

    plt.tight_layout()
    plt.ioff()
    return fig
def plot_CT_MSLP_globe(CT, MSLP, lat_central = 30, lon_central=0):
    '''
    This function plots the 11 circulation types to a map
    ¡! Works only with Basemap module

    :param CT: xarray file of the 27 circulation types
    :param MSLP: a 2D ['lat', 'lon'] DataArray of Mean Sea Level Pressure data in Pa
    *args
    :param lat_central: int -80 to 80
    :param lon_central: int -80 to 80

    '''
    MSLP = JC_functions.renaming_coords(MSLP)

    MSLP = JC_functions.checking_lon_coords(MSLP)
    MSLP = JC_functions.checking_lat_coords(MSLP)

    lat_north = float(CT.lat[-1].values)
    lat_south = float(CT.lat[0].values)
    lon_west  = float(CT.lon[0].values)
    lon_east  = float(CT.lon[-1].values)        

    MSLP = MSLP.sel(lat = slice(lat_south, lat_north), lon = slice(lon_west, lon_east))
    lat = MSLP.lat
    lon = MSLP.lon
    lon_list = list(lon)
    lat_list = list(lat)          
    CT = xr.where((CT.lat < 10) & (CT.lat > -10), np.nan, CT)
    highs = xr.where( (CT>=1) & (CT<=8), 1, np.nan)
    lows = xr.where( (CT>=21) & (CT<=28), 1, np.nan)
    CT = CTs_functions.eleven_CTs(CT)

    #Defining colours to plot CTs
    colores = ListedColormap(["#7C7C77", "#17344F", "#0255F4","#0F78ED", "#9E09EE", "#F6664C",
                         "#F24E64", "#D3C42D", "#2FC698", 
                         "#20E1D7", "#BD0000"])  #C, N, NW, W, SW, S, SE, E, NE, A, LF  
    bounds = np.arange(-1,11,1)
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=12)
    lons, lats = np.meshgrid(CT.lon, CT.lat)
    #Defining size and map boundaries
    # set perspective angle
    fig= plt.figure(figsize = (12,10))
    proj = ccrs.Orthographic(central_longitude = lon_central, central_latitude = lat_central)
    ax = plt.axes(projection=proj)
    ax.coastlines('50m')
    ax.stock_img()
    im1 = plt.pcolor(lons, lats, CT,
                 transform=ccrs.PlateCarree(), norm = norm, cmap = colores, alpha = 0.75)
    from scipy.ndimage.filters import gaussian_filter
    data3 = gaussian_filter(MSLP, sigma=.8)   
    # data3 = np.round(data3,0)
    im2 = plt.contour(lons,lats,data3, 
                     np.arange(1012-40, 1012+44, 4), 
                      transform=ccrs.PlateCarree(), colors = '0.10', linewidths = 0.5)
    ima = plt.contourf(lons, lats, highs, transform=ccrs.PlateCarree(), colors = None, hatches = ['....'], alpha = 0)
    imc = plt.contourf(lons, lats, lows, transform=ccrs.PlateCarree(), colors = None, hatches = ['----'], alpha = 0)


    # plt.clabel(im2, im2.levels, manual = False, inline=True,fmt ='%.0f', fontsize=9)

    legend_elements = [  Line2D([0], [0],marker ='o', color = '#7C7C77',markerfacecolor = None,linestyle='None', markersize = 17,label='LF'),
                         Line2D([0], [0], marker='o', color='#17344F', markerfacecolor=None, linestyle='None', markersize=17, label='A'),
                         Line2D([0], [0], marker='o', color='#0255F4', markerfacecolor=None, linestyle='None', markersize=17, label='NE'),
                         Line2D([0], [0], marker='o', color='#0F78ED', markerfacecolor=None, linestyle='None', markersize=17, label='E'),
                         Line2D([0], [0], marker='o', color='#9E09EE', markerfacecolor=None, linestyle='None', markersize=17, label='SE'),
                         Line2D([0], [0], marker='o', color='#F6664C', markerfacecolor=None, linestyle='None', markersize=17, label='S'),
                         Line2D([0], [0], marker='o', color='#F24E64', markerfacecolor=None, linestyle='None', markersize=17, label='SW'),
                         Line2D([0], [0], marker='o', color='#D3C42D', markerfacecolor=None, linestyle='None', markersize=17, label='W'),
                         Line2D([0], [0], marker='o', color='#2FC698', markerfacecolor=None, linestyle='None', markersize=17, label='NW'),
                         Line2D([0], [0], marker='o', color='#20E1D7', markerfacecolor=None, linestyle='None', markersize=17, label='N'),
                         Line2D([0], [0], marker='o', color='#BD0000', markerfacecolor=None, linestyle='None', markersize=17, label='C'),
                         Line2D([0], [0], marker=None, color ='#000000',markerfacecolor=None, linestyle='--', markersize=17, label='Partly Cyclonic'),
                         Line2D([0], [0], marker=None, color ='#000000',markerfacecolor=None, linestyle='dotted', markersize=17, label='Partly Anticylonic'),                       
                      ]

    plt.legend(handles=legend_elements, loc='right', bbox_to_anchor=(0.90, 0.25, 0.5, 0.5),frameon = False, prop={'size': 14}) #X,Y, LENGTH, WIDHT

    plt.title(str(CT.time.values), size = 16, y = 1.05)

    plt.tight_layout()
    plt.ioff()
    return fig


