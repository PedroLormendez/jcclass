import xarray as xr
import numpy as np


def extract_lat_lon_points(mslp_data: xr.DataArray) -> tuple:
    """
    Extracts latitude and longitude points from the MSLP data within the
    latitude range [-80, 80] degrees.
    Args:
        mslp_data (xr.DataArray): Input MSLP data with standardized coordinates
    Returns:
        tuple: Latitude and Longitude points within the range [-80, 80] degrees

    """
    min_lat, max_lat = (-80.0, 80.0)
    psl_area = mslp_data.where((mslp_data.latitude >= min_lat) & (mslp_data.latitude <= max_lat), drop=True)

    lat = psl_area.latitude
    lon = psl_area.longitude

    return lat, lon


def extracting_gridpoints_area(mslp, latitude, longitude):
    """
    Extracts 16 gridded points over a defined area for a Reanalysis or Global Climate Model dataset.
    These grid points are required for computing terms related to circulation classification.

    The function computes grid points based on predefined latitude and longitude offsets from a central
    point, ensuring that the dataset is not assumed to cover the entire globe.

    Args:
        mslp (xr.DataArray): Mean sea level pressure data with latitude and longitude coordinates.
        latitude (xr.DataArray): Latitude values of the dataset.
        longitude (xr.DataArray): Longitude values of the dataset.

    Returns:
        tuple: A tuple of 16 `numpy.ndarray` objects, each corresponding to a grid point value of `mslp`
               at the calculated latitude and longitude offsets.

    Latitude and Longitude Offsets:
        Grid Point 1:  (+10, -5)
        Grid Point 2:  (+10, +5)
        Grid Point 3:  (+5, -15)
        Grid Point 4:  (+5, -5)
        Grid Point 5:  (+5, +5)
        Grid Point 6:  (+5, +15)
        Grid Point 7:  (+0, -15)
        Grid Point 8:  (+0, -5)
        Grid Point 9:  (+0, +5)
        Grid Point 10: (+0, +15)
        Grid Point 11: (-5, -15)
        Grid Point 12: (-5, -5)
        Grid Point 13: (-5, +5)
        Grid Point 14: (-5, +15)
        Grid Point 15: (-10, -5)
        Grid Point 16: (-10, +5)

    Example:
        >>> latitude = xr.DataArray(np.linspace(-90, 90, 181), dims="latitude", name="latitude")
        >>> longitude = xr.DataArray(np.linspace(-180, 180, 361), dims="longitude", name="longitude")
        >>> mslp = xr.DataArray(np.random.rand(181, 361), coords={"latitude": latitude, "longitude": longitude}, dims=["latitude", "longitude"])
        >>> gridpoints = extracting_gridpoints_area(mslp, latitude, longitude)
        >>> print(gridpoints[0])  # First grid point value
    """
    offsets = [
        (10, -5), (10, 5), (5, -15), (5, -5), (5, 5), (5, 15), (0, -15), (0, -5),
        (0, 5), (0, 15), (-5, -15), (-5, -5), (-5, 5), (-5, 15), (-10, -5), (-10, 5)
    ]
    gridpoints = []

    for lat_offset, lon_offset in offsets:
        lat_point = latitude + lat_offset
        lon_point = longitude + lon_offset

        lat_point = latitude.sel(latitude=lat_point, method="nearest")
        lon_point = longitude.sel(longitude=lon_point, method="nearest")

        gridpoints.append(np.array(mslp.sel(latitude=lat_point, longitude=lon_point)))

    return tuple(gridpoints)


def extracting_gridpoints_globe(mslp, latitude, longitude):
    """
    Extracts 16 gridded points over the entire globe for a Reanalysis or Global Climate Model dataset.
    These grid points are required for computing terms related to circulation classification.

    The function dynamically adjusts longitude values to account for the globe's circular nature
    (longitude wrapping), ensuring that grid points are correctly identified near the 180°E/-180°W boundary.

    Args:
        mslp (xr.DataArray): Mean sea level pressure data with latitude and longitude coordinates.
        latitude (xr.DataArray): Latitude values of the dataset.
        longitude (xr.DataArray): Longitude values of the dataset.

    Returns:
        tuple: A tuple of 16 `numpy.ndarray` objects, each corresponding to a grid point value of `mslp`
               at the calculated latitude and longitude offsets.

    Latitude and Longitude Offsets:
        Grid Point 1:  (+10, -5)
        Grid Point 2:  (+10, +5)
        Grid Point 3:  (+5, -15)
        Grid Point 4:  (+5, -5)
        Grid Point 5:  (+5, +5)
        Grid Point 6:  (+5, +15)
        Grid Point 7:  (+0, -15)
        Grid Point 8:  (+0, -5)
        Grid Point 9:  (+0, +5)
        Grid Point 10: (+0, +15)
        Grid Point 11: (-5, -15)
        Grid Point 12: (-5, -5)
        Grid Point 13: (-5, +5)
        Grid Point 14: (-5, +15)
        Grid Point 15: (-10, -5)
        Grid Point 16: (-10, +5)

    Example:
        >>> latitude = xr.DataArray(np.linspace(-90, 90, 181), dims="latitude", name="latitude")
        >>> longitude = xr.DataArray(np.linspace(-180, 180, 361), dims="longitude", name="longitude")
        >>> mslp = xr.DataArray(np.random.rand(181, 361), coords={"latitude": latitude, "longitude": longitude}, dims=["latitude", "longitude"])
        >>> gridpoints = extracting_gridpoints_globe(mslp, latitude, longitude)
        >>> print(gridpoints[0])  # First grid point value
    """
    offsets = [
        (10, -5), (10, 5), (5, -15), (5, -5), (5, 5), (5, 15), (0, -15), (0, -5),
        (0, 5), (0, 15), (-5, -15), (-5, -5), (-5, 5), (-5, 15), (-10, -5), (-10, 5)
    ]
    gridpoints = []

    for lat_offset, lon_offset in offsets:
        lat_point = latitude + lat_offset
        lon_point = xr.where(
            longitude < -175, 360 + longitude + lon_offset,
            xr.where(longitude > 175, longitude + lon_offset - 360, longitude + lon_offset)
        )
        lon_point = xr.where(lon_point == 180, -180, lon_point)

        lat_point = latitude.sel(latitude=lat_point, method="nearest")
        lon_point = longitude.sel(longitude=lon_point, method="nearest")

        gridpoints.append(np.array(mslp.sel(latitude=lat_point, longitude=lon_point)))

    return tuple(gridpoints)
