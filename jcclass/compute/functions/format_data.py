import xarray as xr


def enhance_and_validate_dataarray(lwt: xr.DataArray) -> xr.DataArray:
    """
    Enhances metadata and validates coordinates for an atmospheric dataset.

    Args:
        lwt (xr.DataArray): The circulation type DataArray.

    Returns:
        xr.DataArray: Enhanced DataArray with added metadata.
    """
    # Set a variable name
    lwt.name = "cts"  # Circulation types (CTS)

    # Add metadata
    lwt.attrs["description"] = "Jenkinson and Collison / Lamb Weather Types (LWT) Classification"
    lwt.attrs["units"] = "categorical"
    lwt.attrs["long_name"] = "Lamb Weather Types"

    # Add metadata to coordinates
    if "latitude" in lwt.coords:
        lwt["latitude"].attrs["units"] = "degrees_north"
        lwt["latitude"].attrs["long_name"] = "Latitude"
    if "longitude" in lwt.coords:
        lwt["longitude"].attrs["units"] = "degrees_east"
        lwt["longitude"].attrs["long_name"] = "Longitude"
    if "time" in lwt.coords:
        lwt["time"].attrs["long_name"] = "Time"
        lwt["time"].attrs["calendar"] = "gregorian"

    # Validate latitude range and order
    if "latitude" in lwt.coords:
        latitude = lwt["latitude"]
        if not (-90 <= latitude.min() <= 90) or not (-90 <= latitude.max() <= 90):
            raise ValueError("Latitude values must range between -90 and 90 degrees.")
        if not (latitude.values[1:] >= latitude.values[:-1]).all():
            raise ValueError("Latitude values must increase monotonically.")

    # Validate longitude range and order
    if "longitude" in lwt.coords:
        longitude = lwt["longitude"]
        if not (-180 <= longitude.min() <= 180) or not (-180 <= longitude.max() <= 180):
            raise ValueError("Longitude values must range between -180 and 180 degrees.")
        if not (longitude.values[1:] >= longitude.values[:-1]).all():
            raise ValueError("Longitude values must increase monotonically.")

    return lwt
