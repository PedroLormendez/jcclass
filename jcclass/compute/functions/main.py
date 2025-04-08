import gc
import numpy as np
import xarray as xr
from .data_preparation import read_mslp_file, checking_lon_coords, \
    checking_lat_coords, is_world
from .data_extraction import extract_lat_lon_points, extracting_gridpoints_area, extracting_gridpoints_globe
from .constants import compute_constants
from .computation import flows, compute_direction, assign_lwt
from .format_data import enhance_and_validate_dataarray

from jcclass.utils.logging_config import setup_logger

logger = setup_logger("jcclass")

def jc_classification(mslp_data: xr.DataArray) -> xr.DataArray:
    logger.info("Starting the computation of the Jenkinson and Collison Circulation Types.")
    # Step 1: Data preparation
    logger.info("Preparing the MSLP data for computation.")
    mslp_data = read_mslp_file(mslp_data)
    mslp_data = checking_lat_coords(mslp_data)
    mslp_data = checking_lon_coords(mslp_data)
    time_data = mslp_data.time
    is_global = is_world(mslp_data)

    logger.info("Extracting grid points.")
    # Step 2: Compute constants
    latitude, longitude = extract_lat_lon_points(mslp_data)
    sc, zwa, zwb, zsc = compute_constants(latitude, longitude)

    if is_global:
        gridpoints = extracting_gridpoints_globe(mslp_data, latitude, longitude)
    else:
        gridpoints = extracting_gridpoints_area(mslp_data, latitude, longitude)

    logger.info("Computing equations of flows and vorticity.")
    # Step 3: Compute equations of flows and vorticity
    W, S, F, ZW, ZS, Z = flows(gridpoints, sc, zwa, zsc, zwb, latitude, longitude, time_data, mslp_data)
    deg = np.mod(180 + np.rad2deg(np.arctan2(W, S)), 360)

    logger.info("Computing flow directions.")
    # Step 4: Compute flow directions
    direction = compute_direction(deg, latitude)

    logger.info("Assigning Lamb Weather Types.")
    # Step 5: Assign Lamb Weather Types
    lwt = assign_lwt(F, Z, direction)

    logger.info("Validating and creating DataArray.")
    # Step 6: Enhance and validate DataArray
    lwt = enhance_and_validate_dataarray(lwt)
    logger.info("Success!")

    return lwt
