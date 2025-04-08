import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from .functions.tools import ensure_2d, crop_area
from .functions.plot_utils import get_cmap_and_norm, add_legend, get_fig_size, \
    configure_gridlines, format_time_string
from jcclass.compute.core import eleven_cts
from jcclass.utils.logging_config import setup_logger
logger = setup_logger("jcclass")


def plot_cts(ds: xr.DataArray,
             lat_south: int = -80,
             lat_north: int = 80,
             lon_west: int = -180,
             lon_east: int = 180,
             show: bool = True):
    """
    Plot the 27 circulation types on a map for a single time step.

    This function visualizes one time slice of circulation types (typically 27 classes)
    using a predefined colormap, with optional geographic cropping. It also masks out
    the equatorial region and converts values to the 11 reduced CT categories.

    Parameters
    ----------
    ds : xr.DataArray
        A 2D `xarray.DataArray` with latitude and longitude dimensions.
        Must represent a single time step of 27 circulation types.

    lat_south : int, optional
        Southern latitude boundary of the map (default: -80).

    lat_north : int, optional
        Northern latitude boundary of the map (default: 80).

    lon_west : int, optional
        Western longitude boundary of the map (default: -180).

    lon_east : int, optional
        Eastern longitude boundary of the map (default: 180).

    show : bool, optional
        Whether to display the plot immediately using `plt.show()`.
        If False, the figure is returned silently (default: True).

    Returns
    -------
    fig : matplotlib.figure.Figure
        The generated figure containing the circulation type map.

    Notes
    -----
    - The equatorial band between -10 and 10 degrees latitude is masked out.
    - A legend showing the 11 reduced CTs is included.
    - The title includes the date (and hour, if available) from the time coordinate.

    Examples
    --------
    >>> from jcclass.plotting import plot_cts
    >>> cts_day = cts_27.sel(time="1979-01-01")
    >>> fig = plot_cts(cts_day, lat_south=-60, lat_north=60, lon_west=-100, lon_east=20)
    >>> fig.savefig("my_cts_map.png")
    """
    logger.info("Plotting the circulation types to a map.")
    # Checking the xr.DataArray is 2D
    ensure_2d(ds)
    # Cropping the area
    ds = crop_area(ds, lat_north, lat_south, lon_west, lon_east)
    # Redefining longitude and latitude limit points
    lat_north = ds.latitude.max()
    lat_south = ds.latitude.min()
    lon_west = ds.longitude.min()
    lon_east = ds.longitude.max()

    # Mask the data to remove the equatorial region
    ds = xr.where((ds.latitude < 10) & (ds.latitude > -10), np.nan, ds)
    # Convert to 11 CTs
    ds = eleven_cts(ds)

    # Get the colormap and normalization
    cmap, norm = get_cmap_and_norm()
    # Compute the size of the figure
    size_x, size_y = get_fig_size(ds)
    # Get the x and y coordinate values
    lons, lats = ds.longitude, ds.latitude

    # Plotting
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(size_x, size_y), subplot_kw={'projection': proj})
    ax.set_extent([lon_west, lon_east, lat_south, lat_north], crs=proj)

    ax.pcolor(lons, lats, ds, transform=proj, norm=norm, cmap=cmap)

    ax.coastlines('50m')
    configure_gridlines(ax)
    add_legend(fig, ax)

    # Add date title if available
    time_string = format_time_string(ds)
    ax.set_title(time_string, size=12, loc='left')

    plt.tight_layout()
    if show:
        plt.show()
    return fig
