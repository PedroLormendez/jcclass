import xarray as xr
import numpy as np


def flows(gridpoints, sc, zwa, zsc, zwb, latitude, longitude, time, mslp_data):
    """
    Computes indices associated with the direction and vorticity of geostrophic flow
    given a reanalysis or GCM dataset.

    Args:
        gridpoints (tuple): A tuple containing the 16 gridded MSLP values (p1 to p16).
        sc (xr.DataArray): Longitudinal scaling factor.
        zwa (xr.DataArray): Zonal weighting factor (latitude - 5 degrees).
        zwb (xr.DataArray): Zonal weighting factor (latitude + 5 degrees).
        zsc (xr.DataArray): Shear constant.
        latitude (xr.DataArray): Latitude values of the dataset.
        longitude (xr.DataArray): Longitude values of the dataset.
        time (xr.DataArray): Time values of the dataset.
        mslp_data (xr.DataArray): Mean sea level pressure dataset.

    Returns:
        tuple: (W, S, F, ZW, ZS, Z)
            W: Westerly flow
            S: Southerly flow
            F: Resultant flow
            ZW: Westerly shear vorticity
            ZS: Southerly shear vorticity
            Z: Total shear vorticity
    """
    # Unpack gridpoints
    (p1, p2, p3, p4, p5, p6, p7, p8,
     p9, p10, p11, p12, p13, p14, p15, p16) = gridpoints

    # Ensure sc, zwa, zsc, and zwb match the dimensions of MSLP
    sc = sc.expand_dims(dim={"time": time}, axis=0)
    zwa = zwa.expand_dims(dim={"time": time}, axis=0)
    zsc = zsc.expand_dims(dim={"time": time}, axis=0)
    zwb = zwb.expand_dims(dim={"time": time}, axis=0)

    # Westerly Flow
    W = (0.5 * (p12 + p13)) - (0.5 * (p4 + p5))
    if mslp_data.dims[1] == "latitude":
        W = xr.DataArray(W, coords={"time": time, "latitude": latitude, "longitude": longitude}, dims=["time", "latitude", "longitude"])
    elif mslp_data.dims[1] == "number":
        W = xr.DataArray(W, coords={"time": time, "number": mslp_data.number, "latitude": latitude, "longitude": longitude}, dims=["time", "number", "latitude", "longitude"])

    # Southerly Flow
    S = sc * ((0.25 * (p5 + 2 * p9 + p13)) - (0.25 * (p4 + 2 * p8 + p12)))
    if mslp_data.dims[1] == "latitude":
        S = xr.DataArray(S, coords={"time": time, "latitude": latitude, "longitude": longitude}, dims=["time", "latitude", "longitude"])
    elif mslp_data.dims[1] == "number":
        S = xr.DataArray(S, coords={"time": time, "number": mslp_data.number, "latitude": latitude, "longitude": longitude}, dims=["time", "number", "latitude", "longitude"])

    # Resultant Flow
    F = np.sqrt(S**2 + W**2)

    # Westerly Shear Vorticity
    ZW = (zwa * (0.5 * (p15 + p16) - 0.5 * (p8 + p9))) - (zwb * (0.5 * (p8 + p9) - 0.5 * (p1 + p2)))
    if mslp_data.dims[1] == "latitude":
        ZW = xr.DataArray(ZW, coords={"time": time, "latitude": latitude, "longitude": longitude}, dims=["time", "latitude", "longitude"])
    elif mslp_data.dims[1] == "number":
        ZW = xr.DataArray(ZW, coords={"time": time, "number": mslp_data.number, "latitude": latitude, "longitude": longitude}, dims=["time", "number", "latitude", "longitude"])

    # Southerly Shear Vorticity
    ZS = zsc * ((0.25 * (p6 + 2 * p10 + p14)) - (0.25 * (p5 + 2 * p9 + p13)) - (0.25 * (p4 + 2 * p8 + p12)) + (0.25 * (p3 + 2 * p7 + p11)))
    if mslp_data.dims[1] == "latitude":
        ZS = xr.DataArray(ZS, coords={"time": time, "latitude": latitude, "longitude": longitude}, dims=["time", "latitude", "longitude"])
    elif mslp_data.dims[1] == "number":
        ZS = xr.DataArray(ZS, coords={"time": time, "number": mslp_data.number, "latitude": latitude, "longitude": longitude}, dims=["time", "number", "latitude", "longitude"])

    # Total Shear Vorticity
    Z = ZW + ZS

    return W, S, F, ZW, ZS, Z


def compute_direction(deg, latitude):
    """
    Assigns wind direction labels based on wind direction degrees and hemisphere.

    Args:
        deg (xr.DataArray): Wind direction values in degrees.
        latitude (xr.DataArray): Latitude values to determine the hemisphere.

    Returns:
        xr.DataArray: Wind direction labels as strings.
    """
    # Define the direction labels for both hemispheres
    nh_labels = {
        "W": (247, 292),
        "NW": (292, 337),
        "N": (337, 22),
        "NE": (22, 67),
        "E": (67, 112),
        "SE": (112, 157),
        "S": (157, 202),
        "SW": (202, 247),
    }

    sh_labels = {
        "E": (247, 292),
        "SE": (292, 337),
        "S": (337, 22),
        "SW": (22, 67),
        "W": (67, 112),
        "NW": (112, 157),
        "N": (157, 202),
        "NE": (202, 247),
    }

    # Initialize direction as NaN
    direction = xr.full_like(deg, fill_value=np.nan, dtype=object)

    # Determine Northern Hemisphere directions
    for label, (lower, upper) in nh_labels.items():
        if lower <= upper:
            direction = xr.where((latitude >= 0) & (deg > lower) & (deg <= upper), label, direction)
        else:  # Handle wrap-around (e.g., N: 337-22)
            direction = xr.where((latitude >= 0) & ((deg > lower) | (deg <= upper)), label, direction)

    # Determine Southern Hemisphere directions
    for label, (lower, upper) in sh_labels.items():
        if lower <= upper:
            direction = xr.where((latitude < 0) & (deg > lower) & (deg <= upper), label, direction)
        else:  # Handle wrap-around (e.g., S: 337-22)
            direction = xr.where((latitude < 0) & ((deg > lower) | (deg <= upper)), label, direction)

    return direction


def assign_lwt(F_i, Z_i, direction_i):
    """
    Assigns circulation type codes (Lamb Weather Types) based on flow and vorticity.

    Args:
        F_i (xr.DataArray): Total flow term (F).
        Z_i (xr.DataArray): Total shear vorticity term (Z).
        direction_i (xr.DataArray): Flow direction.

    Returns:
        xr.DataArray: Circulation type classification for each grid point.
            - Codes range from 0 (purely anticyclonic) to 28 (directional flows).
            - -1 indicates weak/unclassified flow.

    Example:
        >>> lwt = assign_lwt(F, Z, direction)
        >>> print(lwt)
    """
    if not isinstance(F_i, xr.DataArray) or not isinstance(Z_i, xr.DataArray) or not isinstance(direction_i, xr.DataArray):
        raise TypeError("F_i, Z_i, and direction_i must all be xarray.DataArray objects.")

    # Hybrid Anticyclonic flows
    lwt = xr.where((Z_i < 0) & (direction_i == 'NE'), 1, np.nan)
    lwt = xr.where((Z_i < 0) & (direction_i == 'E'), 2, lwt)
    lwt = xr.where((Z_i < 0) & (direction_i == 'SE'), 3, lwt)
    lwt = xr.where((Z_i < 0) & (direction_i == 'S'), 4, lwt)
    lwt = xr.where((Z_i < 0) & (direction_i == 'SW'), 5, lwt)
    lwt = xr.where((Z_i < 0) & (direction_i == 'W'), 6, lwt)
    lwt = xr.where((Z_i < 0) & (direction_i == 'NW'), 7, lwt)
    lwt = xr.where((Z_i < 0) & (direction_i == 'N'), 8, lwt)

    # Hybrid Cyclonic flows
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'NE'), 11, lwt)
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'E'), 12, lwt)
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'SE'), 13, lwt)
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'S'), 14, lwt)
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'SW'), 15, lwt)
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'W'), 16, lwt)
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'NW'), 17, lwt)
    lwt = xr.where((np.abs(Z_i) < F_i) & (direction_i == 'N'), 18, lwt)

    # Purely Cyclonic
    lwt = xr.where((np.abs(Z_i) > (2 * F_i)) & (Z_i > 0), 20, lwt)

    # Purely Anticyclonic
    lwt = xr.where((np.abs(Z_i) > (2 * F_i)) & (Z_i < 0), 0, lwt)

    # Directional flows
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'NE'), 21, lwt)
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'E'), 22, lwt)
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'SE'), 23, lwt)
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'S'), 24, lwt)
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'SW'), 25, lwt)
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'W'), 26, lwt)
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'NW'), 27, lwt)
    lwt = xr.where((np.abs(Z_i) > F_i) & (np.abs(Z_i) < (2 * F_i)) & (Z_i > 0) & (direction_i == 'N'), 28, lwt)

    # Low Flow / Unclassified / Weak Flow
    lwt = xr.where((F_i < 6) & (np.abs(Z_i) < 6), -1, lwt)

    return lwt

