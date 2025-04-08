import numpy as np
import xarray as xr


def compute_constants(phi: xr.DataArray, lon: xr.DataArray) -> tuple:
    """
    Computes constants dependent on latitude and longitude for grid-point spacing.
    These constants represent relative differences in the E-W and N-S grid-point spacing.

    Args:
        phi (xr.DataArray): Central latitude grid points (1D array).
        lon (xr.DataArray): Longitude values (1D array).

    Returns:
        tuple:
            sc (xr.DataArray): Longitudinal scaling factor.
            zwa (xr.DataArray): Zonal weighting factor (latitude - 5 degrees).
            zwb (xr.DataArray): Zonal weighting factor (latitude + 5 degrees).
            zsc (xr.DataArray): Shear constant.
    """
    if not isinstance(phi, xr.DataArray) or not isinstance(lon, xr.DataArray):
        raise TypeError("Both phi (latitude) and lon (longitude) must be xarray.DataArray objects.")

    # Validate dimensions
    if "latitude" not in phi.dims or len(phi.dims) != 1:
        raise ValueError("phi must be a 1D xarray.DataArray with 'latitude' as its dimension.")
    if "longitude" not in lon.dims or len(lon.dims) != 1:
        raise ValueError("lon must be a 1D xarray.DataArray with 'longitude' as its dimension.")

    # Longitudinal scaling factor
    sc = 1 / np.cos(np.deg2rad(phi))
    sc = xr.DataArray(
        np.repeat(sc.values[:, None], len(lon), axis=1),
        coords={"latitude": phi, "longitude": lon},
        dims=["latitude", "longitude"],
        name="sc"
    )

    # Zonal weighting factors
    zwa = np.sin(np.deg2rad(phi)) / np.sin(np.deg2rad(phi - 5))
    zwb = np.sin(np.deg2rad(phi)) / np.sin(np.deg2rad(phi + 5))
    zwa = xr.DataArray(
        np.repeat(zwa.values[:, None], len(lon), axis=1),
        coords={"latitude": phi, "longitude": lon},
        dims=["latitude", "longitude"],
        name="zwa"
    )
    zwb = xr.DataArray(
        np.repeat(zwb.values[:, None], len(lon), axis=1),
        coords={"latitude": phi, "longitude": lon},
        dims=["latitude", "longitude"],
        name="zwb"
    )

    # Shear constant
    zsc = 1 / (2 * (np.cos(np.deg2rad(phi)) ** 2))
    zsc = xr.DataArray(
        np.repeat(zsc.values[:, None], len(lon), axis=1),
        coords={"latitude": phi, "longitude": lon},
        dims=["latitude", "longitude"],
        name="zsc"
    )

    return sc, zwa, zwb, zsc
