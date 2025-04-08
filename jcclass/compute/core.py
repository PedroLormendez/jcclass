import xarray as xr
from .functions.main import jc_classification


def compute_cts(data_mslp: xr.DataArray) -> xr.DataArray:
    """
    Computes the Jenkinson and Collison Circulation Types (CTs) based on
    Mean Sea Level Pressure (MSLP) data.

    Args:
        data_mslp (xr.DataArray): Input MSLP data as an xarray DataArray.
            - Dimensions: Typically includes "time", "latitude", and "longitude".
            - Units: Should be in Pascals (Pa) or Hectopascals (hPa).

    Returns:
        xr.DataArray: Computed circulation types as an xarray DataArray.
            - Dimensions: Same as input, with "time", "latitude", and "longitude".
            - Values: Integer codes representing circulation types.
                - Codes range from 0 to 28, with -1 indicating unclassified flows.
            - Attributes: Includes metadata describing the circulation type calculation.

    Notes:
        - The classification is derived using a gridded version of the Lamb Weather Types.
        - Ensure the input dataset has global or regional coverage with appropriate
          spatial and temporal resolution.

    Example:
        >>> import xarray as xr
        >>> from jcclass.compute.core import compute_cts
        >>> data_mslp = xr.open_dataset("mslp_data.nc").msl
        >>> cts = compute_cts(data_mslp)
        >>> print(cts)
    """
    ds = jc_classification(data_mslp)
    return ds


def eleven_cts(cts: xr.DataArray) -> xr.DataArray:
    """
    Reduces the 27 Lamb Weather Types (LWT) circulation types to 11 types
    based on their advective characteristics.

    Args:
        cts (xr.DataArray): DataArray containing the 27 circulation types.

    Returns:
        xr.DataArray: DataArray with reduced 11 circulation types.

    Example:
        >>> import xarray as xr
        >>> from jcclass.compute.core import eleven_cts
        >>> cts = xr.open_dataset("cts_data.nc").lwt
        >>> cts_11 = eleven_cts(cts)
        >>> print(cts_11)
    """
    mapping = {
        1: [11, 21, 1],   # NE
        2: [12, 22, 2],   # E
        3: [13, 23, 3],   # SE
        4: [14, 24, 4],   # S
        5: [15, 25, 5],   # SW
        6: [16, 26, 6],   # W
        7: [17, 27, 7],   # NW
        8: [18, 28, 8],   # N
        9: [20],          # Cyclonic
    }

    # Apply the mapping
    for reduced_type, original_types in mapping.items():
        cts = xr.where(cts.isin(original_types), reduced_type, cts)

    return cts


