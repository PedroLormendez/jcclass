import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use("TkAgg")  # Use TkAgg for interactive plots

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import cartopy.crs as ccrs

from .tools import calculate_size, define_colormap, configure_gridlines, add_legend
from jcclass.compute.core import eleven_cts
from jcclass.utils.logging_config import setup_logger

logger = setup_logger("jcclass-plotting")

def plot_cts_map(
    CT: xr.DataArray,
    lat_south: int = -80,
    lat_north: int = 80,
    lon_west: int = -180,
    lon_east: int = 180
) -> plt.Figure:
    """
    This function plots the 11 circulation types to a map.

    :param CT: A 2D ['lat', 'lon'] DataArray file of the 27 circulation types.
    :param lat_south: int, default -80 to 80.
    :param lat_north: int, default -80 to 80.
    :param lon_west: int, default -180 to 180.
    :param lon_east: int, default -180 to 180.
    :return: A matplotlib Figure object.
    """
    logger.info("Plotting the circulation types to a map.")
    # Squeeze the DataArray to ensure it's 2D
    CT = CT.squeeze()
    lat_north = CT.latitude.sel(latitude = lat_north, method = 'nearest')
    lat_south = CT.latitude.sel(latitude = lat_south, method = 'nearest')
    lon_west = CT.longitude.sel(longitude = lon_west, method = 'nearest')
    lon_east = CT.longitude.sel(longitude = lon_east, method = 'nearest')
    CT = CT.sel(latitude=slice(lat_south, lat_north), longitude=slice(lon_west, lon_east))
    dif_x = lon_east - lon_west
    dif_y = lat_north - lat_south
    size_x, size_y = calculate_size(dif_x, dif_y)
    CT = xr.where((CT.latitude < 10) & (CT.latitude > -10), np.nan, CT)
    # highs = xr.where( (CT>=1) & (CT<=8), 1, np.nan)
    # lows = xr.where( (CT>=21) & (CT<=28), 1, np.nan)
    CT = eleven_cts(CT)
    #Defining colours to plot CTs
    colores = define_colormap()
    norm = BoundaryNorm(boundaries=np.arange(-1, 11, 1), ncolors=12)
    lons, lats = CT.longitude, CT.latitude
    #Defining size and map boundaries
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(size_x, size_y), subplot_kw={'projection': proj})
    ax.set_extent([lon_west, lon_east, lat_south, lat_north], crs=ccrs.PlateCarree())
    im = ax.pcolor(lons, lats, CT, transform=ccrs.PlateCarree(), norm=norm, cmap=colores)

    ax.coastlines('50m')

    configure_gridlines(ax)
    add_legend(fig, ax)

    # Format and place the title
    date_str = pd.to_datetime(str(CT.time.values)).strftime('%Y-%m-%d')
    plt.title(date_str, size=12, loc='center')
    plt.tight_layout()
    plt.ion()
    plt.show()
    return fig
