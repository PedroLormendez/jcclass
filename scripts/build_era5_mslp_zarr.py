"""
Pull raw mean sea-level pressure from ARCO-ERA5 for exactly the same time
steps and grid already covered by sample_data/era5_cts.zarr, and save it to
its own archive, sample_data/era5_mslp.zarr.

This is a one-shot companion to the CT archive (not append-only / growable
like build_era5_cts_zarr.py) -- it exists so the website can plot MSLP
isobars on top of the circulation types for the same days, for testing.
It reads the CT archive's own valid_time/latitude/longitude coordinates
rather than re-deriving them, so the two archives are guaranteed to line up
exactly.

Requires the same extra packages as build_era5_cts_zarr.py:
    pip install gcsfs zarr dask

Usage:
    python scripts/build_era5_mslp_zarr.py
"""

from datetime import datetime, timezone
from pathlib import Path

import xarray as xr
from zarr.codecs import GzipCodec

ARCO_URL = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
MSLP_VAR = "mean_sea_level_pressure"
TIME_DIM = "valid_time"

REPO_ROOT = Path(__file__).resolve().parent.parent
CTS_PATH = REPO_ROOT / "sample_data" / "era5_cts.zarr"
OUTPUT_PATH = REPO_ROOT / "sample_data" / "era5_mslp.zarr"

CHUNK_TIME = 1  # one hour per chunk, matching era5_cts.zarr's per-timestep fetch pattern


def load_target_grid() -> xr.Dataset:
    """The CT archive's own coordinates -- the MSLP pull matches these exactly."""
    ds = xr.open_zarr(CTS_PATH, consolidated=True)
    return ds[[TIME_DIM, "latitude", "longitude"]]


def load_arco_mslp(times, lats, lons) -> xr.DataArray:
    """Stream just the needed timestamps from ARCO-ERA5 (one HTTP fetch, no full download)."""
    ds = xr.open_zarr(
        ARCO_URL,
        chunks={},
        consolidated=True,
        storage_options={"token": "anon"},
    )
    mslp = ds[MSLP_VAR].sel(time=times)
    # ARCO-ERA5 longitude is 0..360; the CT archive (and jcclass internally)
    # uses -180..180 (see jcclass/compute/functions/data_preparation.py:97-107).
    # Convert before selecting so both archives share one lon convention --
    # mismatched conventions silently misalign an isobar/CT overlay by up to
    # 180 deg (hit this exact bug prototyping the idea earlier this session).
    mslp = mslp.assign_coords(longitude=(((mslp.longitude + 180) % 360) - 180)).sortby("longitude")
    mslp = mslp.sel(latitude=lats, longitude=lons, method="nearest")
    return mslp.load()


def build_dataset(mslp_hpa: xr.DataArray, target: xr.Dataset) -> xr.Dataset:
    mslp_hpa = mslp_hpa.rename({"time": TIME_DIM})
    mslp_hpa = mslp_hpa.transpose(TIME_DIM, "latitude", "longitude")
    # Use the CT archive's own coordinate arrays verbatim (not the
    # nearest-matched ones ARCO-ERA5 handed back) so the two stores' lat/lon
    # are byte-identical, not just numerically close.
    mslp_hpa = mslp_hpa.assign_coords(
        latitude=target.latitude, longitude=target.longitude, **{TIME_DIM: target[TIME_DIM]}
    )
    ds = xr.Dataset({"mslp": mslp_hpa})

    for name in (TIME_DIM, "latitude", "longitude"):
        ds[name].encoding = {}

    ds[TIME_DIM].attrs = {"standard_name": "time", "long_name": "valid time"}
    ds.latitude.attrs = {"standard_name": "latitude", "long_name": "latitude", "units": "degrees_north"}
    ds.longitude.attrs = {"standard_name": "longitude", "long_name": "longitude", "units": "degrees_east"}
    ds.mslp.attrs = {
        "standard_name": "air_pressure_at_mean_sea_level",
        "long_name": "mean sea-level pressure",
        "units": "hPa",
    }
    ds.attrs = {
        "title": "Mean sea-level pressure from ARCO-ERA5, matched to era5_cts.zarr's grid/time",
        "summary": (
            "Raw MSLP (hPa) for exactly the time steps and 0.5 deg grid covered by "
            "era5_cts.zarr, for prototyping isobar overlays on the site. One-shot, "
            "not append-only; see scripts/build_era5_mslp_zarr.py."
        ),
        "source": f"{ARCO_URL} :: {MSLP_VAR}",
        "Conventions": "CF-1.8",
        "references": "https://github.com/PedroLormendez/jcclass",
        "history": f"Created {datetime.now(timezone.utc).isoformat(timespec='seconds')} with scripts/build_era5_mslp_zarr.py",
    }
    return ds


def main() -> None:
    print(f"Reading target grid/time from {CTS_PATH} ...")
    target = load_target_grid()
    ntime = target.sizes[TIME_DIM]
    print(
        f"  {ntime} time step(s) [{target[TIME_DIM].values.min()} .. {target[TIME_DIM].values.max()}], "
        f"grid {target.sizes['latitude']}x{target.sizes['longitude']}"
    )

    print(f"Streaming {MSLP_VAR} from ARCO-ERA5 for those {ntime} step(s) ...")
    mslp_pa = load_arco_mslp(target[TIME_DIM].values, target.latitude.values, target.longitude.values)
    mslp_hpa = mslp_pa / 100.0
    print(f"  fetched shape={dict(mslp_hpa.sizes)}, ~{mslp_hpa.nbytes / 1e6:.1f} MB")

    ds = build_dataset(mslp_hpa, target)

    print(f"Writing to {OUTPUT_PATH} ...")
    nlat, nlon = ds.sizes["latitude"], ds.sizes["longitude"]
    encoding = {
        "mslp": {
            "dtype": "float32",
            "chunks": (CHUNK_TIME, nlat, nlon),
            "compressors": [GzipCodec(level=6)],
        }
    }
    ds.to_zarr(OUTPUT_PATH, mode="w", consolidated=True, encoding=encoding)

    size_bytes = sum(f.stat().st_size for f in OUTPUT_PATH.rglob("*") if f.is_file())
    print(f"Done. {OUTPUT_PATH} ({size_bytes / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
