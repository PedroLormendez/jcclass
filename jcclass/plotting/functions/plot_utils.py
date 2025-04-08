import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker


def get_cmap_and_norm():
    """
    Returns the colormap and normalization used to plot 11 circulation types.

    Returns:
        cmap (ListedColormap): Colormap for circulation types.
        norm (BoundaryNorm): Boundary norm to map values to colors.
    """
    cmap = ListedColormap([
        "#7C7C77", "#17344F", "#0255F4", "#0F78ED", "#9E09EE", "#F6664C",
        "#F24E64", "#D3C42D", "#2FC698", "#20E1D7", "#BD0000"
    ])
    norm = BoundaryNorm(boundaries=np.arange(-1, 11, 1), ncolors=12)

    return cmap, norm


def get_fig_size(ds: xr.DataArray) -> tuple:
    """
    Calculate the size of the figure based on the area of interest.
    parameters:
        ds (xarray.DataArray): DataArray containing latitude and longitude coordinates.
    returns:
        tuple: Size of the figure in inches (width, height).
    """
    lat_north = ds.latitude.max()
    lat_south = ds.latitude.min()
    lon_west = ds.longitude.min()
    lon_east = ds.longitude.max()
    # Calculate the size of the figure based on the area of interest
    dif_x = lon_east - lon_west
    dif_y = lat_north - lat_south
    size_x, size_y = 12, 10
    if dif_x > dif_y:
        size_y = size_x * (dif_y / dif_x)
    elif dif_x < dif_y:
        size_x = size_y * (dif_x / dif_y)
    return size_x, size_y


def configure_gridlines(ax: plt.Axes) -> None:
    """
    Adds formatted geographic gridlines to a Cartopy axis.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        The axis (with Cartopy projection) to which the gridlines will be added.

    Notes
    -----
    - Latitude labels are shown on the left.
    - Longitude labels are shown at the bottom.
    - Gridlines themselves are hidden (no xlines or ylines), only labels are displayed.
    - Gridline locators and formatters are fixed to common global coordinates.
    """
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True)
    gl.top_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = False
    gl.xlines = False  # disables grid lines
    gl.ylines = False
    gl.ylocator = mticker.FixedLocator([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    gl.xlocator = mticker.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER


def add_legend(fig: plt.Figure, ax: plt.Axes) -> None:
    """
    Adds a custom legend for 11 circulation types to the plot.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure object where the legend will be attached.

    ax : matplotlib.axes.Axes
        The axis object to which the legend belongs.

    Notes
    -----
    - The legend includes 11 circulation types labeled:
      ['LF', 'A', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'C']
    - Colors correspond to the colormap used in the circulation plot.
    - The legend is placed outside the plot at the center right.
    """
    legend_labels = ['LF', 'A', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N', 'C']
    legend_colors = [
        "#7c7c77", "#1c2c4b", "#123FDD", "#245cdc", "#802fcd", "#d98b4f",
        "#D17860", "#d0c742", "#4d9f9e", "#46afd8", "#973000"
    ]
    legend_styles = ['None'] * 11  # Only markers, no lines

    legend_elements = [
        Line2D([0], [0], marker='o', color=color, linestyle=style, markersize=16, label=label)
        for color, style, label in zip(legend_colors, legend_styles, legend_labels)
    ]

    ax.legend(
        handles=legend_elements,
        loc='center right',
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
        prop={'size': 14},
        bbox_transform=fig.transFigure
    )


def format_time_string(ds: xr.DataArray) -> str:
    """
    Returns a formatted time string from the 'time' or 'valid_time' coordinate.
    Includes hours if present (e.g., for hourly data).

    Parameters
    ----------
    ds : xr.DataArray
        DataArray that contains a 'time' or 'valid_time' coordinate.

    Returns
    -------
    str
        A formatted time string, e.g., '2025-04-06' or '2025-04-06 18:00'.

    Raises
    ------
    ValueError
        If neither 'time' nor 'valid_time' coordinate is found.
    """
    # Try to find time coordinate
    for time_coord in ['time', 'valid_time']:
        if time_coord in ds.coords:
            time_val = ds[time_coord].values
            break
    else:
        raise ValueError("No 'time' or 'valid_time' coordinate found.")

    # Convert to pandas datetime (supporting scalar or array)
    time_val = pd.to_datetime(time_val)

    if isinstance(time_val, (np.ndarray, pd.DatetimeIndex)):
        time_val = time_val[0]

    # Include hour if not 00:00
    if time_val.hour != 0 or time_val.minute != 0:
        return time_val.strftime('%Y-%m-%d %H:%M')
    else:
        return time_val.strftime('%Y-%m-%d')

