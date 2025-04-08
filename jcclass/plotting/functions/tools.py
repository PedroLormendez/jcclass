import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.colors as colors
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker

from jcclass.compute.core import eleven_cts


def calculate_size(dif_x: float, dif_y: float) -> tuple:
    size_x, size_y = 12, 10
    if dif_x > dif_y:
        size_y = size_x * (dif_y / dif_x)
    elif dif_x < dif_y:
        size_x = size_y * (dif_x / dif_y)
    return size_x, size_y


def define_colormap() -> ListedColormap:
    return ListedColormap([
        "#7C7C77", "#17344F", "#0255F4", "#0F78ED", "#9E09EE", "#F6664C",
        "#F24E64", "#D3C42D", "#2FC698", "#20E1D7", "#BD0000"
    ])


def configure_gridlines(ax: plt.Axes) -> None:
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
    gl.top_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = False
    gl.xlines = False
    gl.ylines = False
    gl.ylocator = mticker.FixedLocator([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    gl.xlocator = mticker.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER


def add_legend(fig: plt.Figure, ax: plt.Axes) -> None:
    legend_labels = ['LF', 'A', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'C']
    legend_colors = ["#7c7c77", "#1c2c4b", "#123FDD", "#245cdc", "#802fcd", "#d98b4f",
                         "#D17860", "#d0c742", "#4d9f9e",
                         "#46afd8", "#973000"]
    legend_styles = ['None'] * 11

    legend_elements = [
        Line2D([0], [0], marker='o', color=color, linestyle=style, markersize=16, label=label)
        for color, style, label in zip(legend_colors, legend_styles, legend_labels)
    ]

    ax.legend(handles=legend_elements, loc='center right', bbox_to_anchor=(1.0, 0.5), frameon=False,
              prop={'size': 14}, bbox_transform=fig.transFigure)

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
    # Squeeze the DataArray to ensure it's 2D
    CT = CT.squeeze()
    lat_north = CT.lat.sel(lat = lat_north, method = 'nearest')
    lat_south = CT.lat.sel(lat = lat_south, method = 'nearest')
    lon_west = CT.lon.sel(lon = lon_west, method = 'nearest')
    lon_east = CT.lon.sel(lon = lon_east, method = 'nearest')
    CT = CT.sel(lat=slice(lat_south, lat_north), lon=slice(lon_west, lon_east))
    dif_x = lon_east - lon_west
    dif_y = lat_north - lat_south
    size_x, size_y = calculate_size(dif_x, dif_y)
    CT = xr.where((CT.lat < 10) & (CT.lat > -10), np.nan, CT)
    # highs = xr.where( (CT>=1) & (CT<=8), 1, np.nan)
    # lows = xr.where( (CT>=21) & (CT<=28), 1, np.nan)
    CT = eleven_cts(CT)
    #Defining colours to plot CTs
    colores = define_colormap()
    norm = BoundaryNorm(boundaries=np.arange(-1, 11, 1), ncolors=12)
    lons, lats = CT.lon, CT.lat
    #Defining size and map boundaries
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(size_x, size_y), subplot_kw={'projection': proj})
    ax.set_extent([lon_west, lon_east, lat_south, lat_north], crs=ccrs.PlateCarree())
    im = ax.pcolor(lons, lats, CT, transform=ccrs.PlateCarree(), norm=norm, cmap=colores)
    # ax.contourf(lons, lats, highs, colors=None, hatches=['....'], alpha=0, transform=ccrs.PlateCarree())
    # ax.contourf(lons, lats, lows, colors=None, hatches=['----'], alpha=0, transform=ccrs.PlateCarree())

    ax.coastlines('50m')

    configure_gridlines(ax)
    add_legend(fig, ax)

    # Format and place the title
    date_str = pd.to_datetime(str(CT.time.values)).strftime('%Y-%m-%d')
    plt.title(date_str, size=12, loc='center')
    plt.tight_layout()
    plt.ioff()
    plt.show()
    return fig




