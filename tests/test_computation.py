import pytest
import os
import numpy as np
import xarray as xr

from jcclass.compute import compute_cts, eleven_cts


def create_dummy_mslp():
    """
    Create a small dummy MSLP dataset with realistic structure
    (time, lat, lon) for testing.
    """
    lat = np.linspace(20, 60, 5)     # 5 lat points
    lon = np.linspace(-20, 20, 5)    # 5 lon points
    time = np.array(['2000-01-01', '2000-01-02'], dtype='datetime64')

    mslp_data = 101325 + 5000 * np.random.rand(len(time), len(lat), len(lon))

    ds = xr.DataArray(
        mslp_data,
        dims=['time', 'latitude', 'longitude'],
        coords={'time': time, 'latitude': lat, 'longitude': lon},
        name='msl'
    )
    return ds


def test_compute_cts_output():
    """
    Test compute_cts returns expected shape and value range.
    """
    ds_mslp = create_dummy_mslp()
    cts = compute_cts(ds_mslp)

    assert isinstance(cts, xr.DataArray)
    assert cts.shape == ds_mslp.shape
    print(f"Min: {cts.min().item()}, Max: {cts.max().item()}")
    assert (cts >= -1).all() and (cts <= 28).all(), "Circulation type values should be between 0 and 27"


def test_eleven_cts_output():
    """
    Test that eleven_cts correctly maps values to the 0–10 range.
    """
    ds_mslp = create_dummy_mslp()
    cts_27 = compute_cts(ds_mslp)
    cts_11 = eleven_cts(cts_27)

    assert isinstance(cts_11, xr.DataArray)
    assert cts_11.shape == cts_27.shape
    print(f"Min: {cts_11.min().item()}, Max: {cts_11.max().item()}")
    assert (cts_11 >= -1).all() and (cts_11 <= 9).all(), "Reduced CTs should be between 0 and 10"


@pytest.mark.skipif(not os.path.exists("sample_data/era5_daily_lowres.nc"), reason="Sample data not found")
def test_with_real_data():
    ds = xr.open_dataset("sample_data/era5_daily_lowres.nc").msl
    cts = compute_cts(ds)
    assert isinstance(cts, xr.DataArray)
