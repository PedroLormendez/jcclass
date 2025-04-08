import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from jcclass.utils.logging_config import setup_logger
logger = setup_logger("jcclass")


def ensure_2d(data: xr.DataArray) -> xr.DataArray:
    """
    Ensure the DataArray is 2D (after squeezing singleton dims).
    If not, raise an error and stop plotting.

    Parameters:
        data (xr.DataArray): The input DataArray.

    Returns:
        xr.DataArray: A squeezed 2D DataArray ready for plotting.

    Raises:
        ValueError: If the resulting DataArray is not 2D.
    """
    squeezed = data.squeeze()

    if squeezed.ndim != 2:
        msg = (
            f"The DataArray has {squeezed.ndim} dimensions after squeezing "
            f"({list(squeezed.dims)}). Only 2D DataArrays can be plotted."
        )
        logger.error(msg)
        raise ValueError(msg)

    return squeezed


def crop_area(data: xr.DataArray,
              lat_north: float,
              lat_south: float,
              lon_west: float,
              lon_east: float) -> xr.DataArray:
    """
    Crop the DataArray to the specified area.
    Parameters:
        data (xr.DataArray): The DataArray to crop.
        lat_north (str): The northern latitude boundary.
        lat_south (str): The southern latitude boundary.
        lon_west (str): The western longitude boundary.
        lon_east (str): The eastern longitude boundary.
    """
    lat_north = data.latitude.sel(latitude=lat_north, method='nearest')
    lat_south = data.latitude.sel(latitude=lat_south, method='nearest')
    lon_west = data.longitude.sel(longitude=lon_west, method='nearest')
    lon_east = data.longitude.sel(longitude=lon_east, method='nearest')
    data = data.sel(latitude=slice(lat_south, lat_north), longitude=slice(lon_west, lon_east))
    return data


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
