import xarray as xr
import numpy as np


def read_mslp_file(mslp_data: xr.DataArray) -> xr.DataArray:
    """
    Validates that the input is an xarray.DataArray containing Mean Sea Level Pressure (MSLP) data,
    and ensures the coordinates are named 'time', 'latitude', and 'longitude'.
    Args:
        mslp_data (xr.DataArray): Input MSLP data as an xarray.DataArray
    Returns:
        xr.DataArray: Validated and standardized MSLP data with proper coordinate names
    Raises:
        TypeError: If the input is not an xarray.DataArray
        ValueError: If the DataArray does not have valid dimensions
    """
    if not isinstance(mslp_data, xr.DataArray):
        raise TypeError("The input must be an xarray.DataArray containing MSLP data.")

    # Coordinate mapping to enforce naming conventions
    coord_mapping = {
        "time": "time",           # Ensure time is named 'time'
        "valid_time": "time",     # Rename valid_time -> time
        "lat": "latitude",        # Rename lat -> latitude
        "latitude": "latitude",   # Ensure latitude stays as latitude
        "lon": "longitude",       # Rename lon -> longitude
        "longitude": "longitude", # Ensure longitude stays as longitude
    }

    # Rename coordinates to enforce naming conventions
    for old_coord, new_coord in coord_mapping.items():
        if old_coord in mslp_data.coords and new_coord != old_coord:
            mslp_data = mslp_data.rename({old_coord: new_coord})

    # Ensure required dimensions
    required_dims = {"time", "latitude", "longitude"}
    if not required_dims.issubset(set(coord_mapping.get(dim, dim) for dim in mslp_data.dims)):
        raise ValueError(
            f"The DataArray must have dimensions: {', '.join(required_dims)}. "
            f"Found: {', '.join(mslp_data.dims)}."
        )

    return mslp_data


def standardize_mslp_units(mslp_data: xr.DataArray) -> xr.DataArray:
    """
    Ensures MSLP is in hectopascals (hPa), converting from Pascals (Pa) if needed.

    ERA5 and most reanalysis/GCM sources store MSLP in Pa (~101325 Pa at sea
    level), but the classification thresholds in assign_lwt -- notably the
    Low Flow rule (F < 6 and |Z| < 6) -- are calibrated for hPa-scale
    pressure differences. Left unconverted, F and Z come out ~100x too
    large, so the Low Flow threshold is essentially never satisfied: every
    other circulation type is a ratio between F and Z and so is unaffected
    by a uniform scale error, but Low Flow uses an absolute threshold and
    was silently almost never assigned as a result.

    Sea-level pressure is physically always ~850-1100 hPa or ~85000-110000
    Pa -- the two ranges never overlap -- so checking the data's own
    magnitude reliably tells Pa from hPa without depending on a `units`
    attribute that may be missing or wrong. This is also what compute_cts's
    docstring already documents ("Should be in Pascals (Pa) or Hectopascals
    (hPa)"); this is what actually makes that promise true.

    Args:
        mslp_data (xr.DataArray): MSLP data, in either Pa or hPa.
    Returns:
        xr.DataArray: MSLP data in hPa.
    """
    mean_magnitude = float(np.abs(mslp_data).mean())
    if mean_magnitude > 10000:
        mslp_data = mslp_data / 100.0
        mslp_data.attrs["units"] = "hPa"
    return mslp_data


def checking_lat_coords(mslp_data: xr.DataArray) -> xr.DataArray:
    """
    Ensures the latitude coordinate values are in ascending order (e.g., -90 to 90º).

    Args:
        mslp_data (xr.DataArray): Input MSLP data with standardized coordinates
    Returns:
        xr.DataArray: MSLP data with latitude coordinate in ascending order
    """
    if mslp_data.latitude[0] > mslp_data.latitude[-1]:
        mslp_data = mslp_data.reindex(latitude=list(reversed(mslp_data.latitude)))
    else:
        pass

    return mslp_data


def checking_lon_coords(mslp_data: xr.DataArray) -> xr.DataArray:
    """
    Ensures the longitude coordinate values are within the range [-180, 180].

    Args:
        mslp_data (xr.DataArray): Input MSLP data with standardized coordinates
    Returns:
        xr.DataArray: MSLP data with longitude coordinate adjusted to [-180, 180]
    """
    if mslp_data.longitude[-1] > 180:
        # Adjust longitude values
        mslp_data['_longitude_adjusted'] = xr.where(
            mslp_data.longitude > 180,
            mslp_data.longitude - 360,
            mslp_data.longitude
        )
        # Swap dimensions and sort
        mslp_data = (
            mslp_data
            .swap_dims({"longitude": "_longitude_adjusted"})
            .sel(_longitude_adjusted=sorted(mslp_data._longitude_adjusted))
            .drop_vars("longitude")
            .rename({"_longitude_adjusted": "longitude"})
        )
    else:
        pass

    return mslp_data


def is_world(mslp_data: xr.DataArray) -> bool:
    """
    Checks if the dataset covers the entire globe based on longitude and latitude coverage.

    Args:
        mslp_data (xr.DataArray or xr.Dataset): Input data with 'longitude' and 'latitude' coordinates.
    Returns:
        bool: True if the dataset covers the entire globe, False otherwise.
    """
    # Calculate the difference between the first two longitude and latitude values
    dif_lon = np.abs(mslp_data.longitude[0] - mslp_data.longitude[1])
    dif_lat = np.abs(mslp_data.latitude[0] - mslp_data.latitude[1])

    # Define conditions for global coverage
    condition_east = mslp_data.longitude[-1] >= (180 - dif_lon)  # Covers up to 180°E
    condition_west = mslp_data.longitude[0] <= (-180 + dif_lon)  # Covers up to 180°W

    is_global = condition_west and condition_east

    return bool(is_global)


