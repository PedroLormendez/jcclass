import pytest
import numpy as np
import xarray as xr
import matplotlib.figure as mplfig

from jcclass.compute import compute_cts
from jcclass.plotting import plot_cts


def create_dummy_cts_2d():
    """
    Create a dummy 2D DataArray representing 27 circulation types.
    """
    lat = np.linspace(-80, 80, 10)
    lon = np.linspace(-180, 180, 10)
    ct_data = np.random.randint(0, 28, size=(10, 10))

    da = xr.DataArray(
        ct_data,
        dims=["latitude", "longitude"],
        coords={"latitude": lat, "longitude": lon},
        name="cts"
    )
    # Add a time coord for the title
    da = da.expand_dims(time=[np.datetime64("2000-01-01T00:00:00")])
    return da.squeeze()


def test_plot_cts_returns_figure():
    """
    Test that plot_cts runs without error and returns a matplotlib Figure.
    """
    cts_2d = create_dummy_cts_2d()
    fig = plot_cts(cts_2d, show=False)

    assert isinstance(fig, mplfig.Figure), "plot_cts should return a matplotlib Figure"


def test_plot_cts_with_custom_area(tmp_path):
    cts_2d = create_dummy_cts_2d()
    fig = plot_cts(cts_2d, lat_south=-60, lat_north=60, lon_west=-100, lon_east=20, show=False)
    path = tmp_path / "test_plot.png"
    fig.savefig(path)
    assert path.exists(), "Figure should be saved to file"

