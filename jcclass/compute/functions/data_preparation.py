import xarray as xr
import logging

logger = logging.getLogger("jcclass.compute.functions.io")
logger.setLevel(logging.INFO)


def read_mslp_file(mslp_data: xr.DataArray) -> xr.DataArray:
    """
    Reads a NetCDF file and extracts the Mean Sea Level Pressure (MSLP) variable.
    Args:
        mslp_data (xr.DataArray): Input M
    Returns:
        xr.DataArray: DataArray containing the MSLP data
    Raises:
        ValueError: If MSLP variable is not found
        TypeError: If the input is not a string
    """
    if not isinstance(mslp_data, xr.DataArray):
        logger.error("Input is not an xarray.DataArray.")
        raise TypeError("The input must be an xarray.DataArray containing MSLP data.")

    logger.info(f"Validating MSLP DataArray....")
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
            logger.info(f"Renaming coordinate '{old_coord}' to '{new_coord}'...")
            mslp_data = mslp_data.rename({old_coord: new_coord})

    # Ensure required dimensions
    required_dims = {"time", "latitude", "longitude"}
    if not required_dims.issubset(set(coord_mapping.get(dim, dim) for dim in mslp_data.dims)):
        logger.error("Missing required dimensions 'time', 'latitude', 'longitude'.")
        raise ValueError(
            f"The DataArray must have dimensions: {', '.join(required_dims)}. "
            f"Found: {', '.join(mslp_data.dims)}."
        )

    logger.info("MSLP DataArray validated successfully.")
    return mslp_data
