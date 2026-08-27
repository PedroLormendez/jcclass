import numpy as np
import xarray as xr
from .data_preparation import read_mslp_file, checking_lon_coords, \
    checking_lat_coords, is_world, standardize_mslp_units
from .data_extraction import extract_lat_lon_points, extracting_gridpoints_area, extracting_gridpoints_globe
from .constants import compute_constants
from .computation import flows, compute_direction, assign_lwt
from .format_data import enhance_and_validate_dataarray
from tqdm import tqdm

from jcclass.utils.logging_config import setup_logger

logger = setup_logger("jcclass")


def jc_classification(mslp_data: xr.DataArray) -> xr.DataArray:
    steps = [
        "Preparing MSLP data",
        "Extracting grid points",
        "Computing flows & vorticity",
        "Computing flow directions",
        "Assigning circulation types",
        "Validating output",
    ]

    with tqdm(total=len(steps), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}",
              colour="cyan", ncols=72) as pbar:

        # Step 1: Data preparation
        pbar.set_postfix_str(steps[0])
        mslp_data = read_mslp_file(mslp_data)
        mslp_data = standardize_mslp_units(mslp_data)
        mslp_data = checking_lat_coords(mslp_data)
        mslp_data = checking_lon_coords(mslp_data)
        time_data = mslp_data.time
        is_global = is_world(mslp_data)
        pbar.update(1)

        # Step 2: Compute constants
        pbar.set_postfix_str(steps[1])
        latitude, longitude = extract_lat_lon_points(mslp_data)
        sc, zwa, zwb, zsc = compute_constants(latitude, longitude)

        if is_global:
            gridpoints = extracting_gridpoints_globe(mslp_data, latitude, longitude)
        else:
            gridpoints = extracting_gridpoints_area(mslp_data, latitude, longitude)
        pbar.update(1)

        # Step 3: Compute equations of flows and vorticity
        pbar.set_postfix_str(steps[2])
        W, S, F, ZW, ZS, Z = flows(gridpoints, sc, zwa, zsc, zwb, latitude, longitude, time_data, mslp_data)
        deg = np.mod(180 + np.rad2deg(np.arctan2(W, S)), 360)
        pbar.update(1)

        # Step 4: Compute flow directions
        pbar.set_postfix_str(steps[3])
        direction = compute_direction(deg, latitude)
        pbar.update(1)

        # Step 5: Assign Lamb Weather Types
        pbar.set_postfix_str(steps[4])
        lwt = assign_lwt(F, Z, direction)
        pbar.update(1)

        # Step 6: Enhance and validate DataArray
        pbar.set_postfix_str(steps[5])
        lwt = enhance_and_validate_dataarray(lwt)
        pbar.update(1)
        pbar.set_postfix_str("Done ✓")

    return lwt
