"""
Build/extend a Zarr archive of reduced (11-type) Jenkinson-Collison circulation
types from ARCO-ERA5.

Reads mean sea-level pressure from the public ARCO-ERA5 Zarr store on Google
Cloud Storage, computes the 27-type classification internally, masks the
equator, reduces to the 11-type scheme with jcclass, and writes only the
11-type result to sample_data/era5_cts.zarr — the 27-type intermediate is
not persisted (the 11-type is what the website plots).

This archive is meant to grow over time: each run selects every hourly
timestamp in ARCO-ERA5 between --start 00:00 and --end 23:00 and appends it
along the `valid_time` dimension. Chunked one hour per chunk and
gzip-compressed, so a static site can fetch a single time step's data with
one HTTP request without needing a server.

Runs are chronological-append-only: a run must start strictly after the
latest timestamp already in the store. Backfilling an earlier gap needs a
separate, deliberate process (not handled here).

Requires extra packages not part of jcclass itself:
    pip install gcsfs zarr dask

Usage:
    python scripts/build_era5_cts_zarr.py --start 2010-09-10 --end 2010-09-20
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from zarr.codecs import GzipCodec

import jcclass
from jcclass import compute_cts, eleven_cts

ARCO_URL = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
MSLP_VAR = "mean_sea_level_pressure"
TIME_DIM = "valid_time"

# Thin the native 0.25 deg grid before classifying. jcclass's neighbour search
# uses fixed +-5 deg offsets regardless of input resolution (see
# notebooks/tutorial_era5_arco.ipynb), so thinning the input is equivalent to
# classifying at full resolution and downsampling the result, just cheaper.
# step=2 -> ~0.5 deg, the resolution the site is built around. Keep this fixed
# across runs -- changing it mid-archive mixes resolutions in one store.
THIN_STEP = 2

CHUNK_TIME = 1  # one hour per chunk, matching the site's per-timestep fetch pattern

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "sample_data" / "era5_cts.zarr"

# Exact codes as produced by jcclass/compute/core.py::eleven_cts
CTS11_FLAG_VALUES = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
CTS11_FLAG_MEANINGS = "LF A NE E SE S SW W NW N C"

FILL_VALUE = -128


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--start", required=True, help="First date, inclusive (YYYY-MM-DD)")
    p.add_argument("--end", required=True, help="Last date, inclusive (YYYY-MM-DD)")
    return p.parse_args()


def hourly_timestamps(start: str, end: str) -> pd.DatetimeIndex:
    return pd.date_range(f"{start} 00:00", f"{end} 23:00", freq="h")


def load_arco_mslp(timestamps: pd.DatetimeIndex, thin_step: int) -> xr.DataArray:
    """Lazily open ARCO-ERA5 and return a loaded MSLP slice, thinned in space."""
    ds = xr.open_zarr(
        ARCO_URL,
        chunks={},
        consolidated=True,
        storage_options={"token": "anon"},
    )
    mslp = ds[MSLP_VAR].sel(time=timestamps)
    mslp = mslp.isel(
        latitude=slice(None, None, thin_step),
        longitude=slice(None, None, thin_step),
    )
    return mslp.load()


def compute_cts11(mslp: xr.DataArray) -> xr.DataArray:
    """27-type classification -> mask equator -> reduce to 11 types.

    The equatorial mask matches jcclass.plotting.core.plot_cts: the method
    needs a Coriolis term that vanishes at the equator, so +-10 deg is
    unreliable and is masked out before the 11-type reduction, exactly like
    the plotting path. The 27-type array itself is not returned/persisted.
    """
    cts_27 = compute_cts(mslp)
    cts_27 = xr.where((cts_27.latitude < 10) & (cts_27.latitude > -10), np.nan, cts_27)
    return eleven_cts(cts_27)


def build_dataset(cts_11: xr.DataArray) -> xr.Dataset:
    """Assemble a CF-ish single-variable Dataset on the valid_time dimension."""
    cts_11 = cts_11.rename({"time": TIME_DIM})
    # Force axis order explicitly -- compute_cts/eleven_cts don't guarantee
    # dimension order, and the chunk encoding below assumes (time, lat, lon)
    # so that one chunk covers one time step (the site's per-fetch unit).
    cts_11 = cts_11.transpose(TIME_DIM, "latitude", "longitude")
    ds = xr.Dataset({"cts_11": cts_11})

    # ARCO-ERA5's coordinates carry their own source .encoding (zarr-v2-style
    # Blosc compressor, full-length chunk sizes), which rides along through
    # isel/load/compute_cts/eleven_cts onto these coordinates. zarr v3's array
    # creation rejects that codec type outright, so drop it -- we want these
    # coordinate arrays written with plain defaults, not the source's encoding.
    for name in (TIME_DIM, "latitude", "longitude"):
        ds[name].encoding = {}

    ds[TIME_DIM].attrs = {"standard_name": "time", "long_name": "valid time"}
    ds.latitude.attrs = {"standard_name": "latitude", "long_name": "latitude", "units": "degrees_north"}
    ds.longitude.attrs = {"standard_name": "longitude", "long_name": "longitude", "units": "degrees_east"}

    ds.cts_11.attrs = {
        "long_name": "Jenkinson-Collison circulation type, reduced (11-class)",
        "flag_values": np.array(CTS11_FLAG_VALUES, dtype="int8"),
        "flag_meanings": CTS11_FLAG_MEANINGS,
        "comment": "Reduced from the 27-type classification by jcclass.eleven_cts; equatorial band masked.",
    }

    ds.attrs = {
        "title": "Jenkinson-Collison circulation types (reduced, 11-class) from ARCO-ERA5",
        "summary": (
            "Hourly reduced 11-type Jenkinson-Collison circulation type "
            "classification computed from ARCO-ERA5 mean sea-level pressure, "
            "thinned to ~0.5 deg resolution. Grown incrementally by appending "
            "along valid_time; see scripts/build_era5_cts_zarr.py."
        ),
        "source": f"{ARCO_URL} :: {MSLP_VAR}, isel step={THIN_STEP}",
        "method": (
            "Jenkinson AF, Collison FP (1977); gridded implementation per "
            "Otero N, Sillmann J, Butler T (2018), doi:10.1007/s00382-017-3705-y"
        ),
        "Conventions": "CF-1.8",
        "references": "https://github.com/PedroLormendez/jcclass",
        "history": (
            f"Created/updated {datetime.now(timezone.utc).isoformat(timespec='seconds')} "
            f"with jcclass {jcclass.__version__} (scripts/build_era5_cts_zarr.py)"
        ),
    }
    return ds


def write_or_append(ds: xr.Dataset, path: Path) -> xr.Dataset:
    if not path.exists():
        nlat, nlon = ds.sizes["latitude"], ds.sizes["longitude"]
        encoding = {
            "cts_11": {
                "dtype": "int8",
                "_FillValue": FILL_VALUE,
                "chunks": (CHUNK_TIME, nlat, nlon),
                "compressors": [GzipCodec(level=9)],
            }
        }
        ds.to_zarr(path, mode="w", consolidated=True, encoding=encoding)
        print(f"  created new store at {path}")
    else:
        existing = xr.open_zarr(path)

        if existing.sizes["latitude"] != ds.sizes["latitude"] or existing.sizes["longitude"] != ds.sizes["longitude"]:
            raise ValueError(
                f"Grid mismatch: existing store is {existing.sizes['latitude']}x{existing.sizes['longitude']}, "
                f"new data is {ds.sizes['latitude']}x{ds.sizes['longitude']}. THIN_STEP must have changed -- "
                "can't append onto a differently-shaped archive."
            )

        existing_times = existing[TIME_DIM].values
        if len(existing_times) > 0:
            existing_max = pd.Timestamp(existing_times.max())
            new_min = pd.Timestamp(ds[TIME_DIM].values.min())
            if new_min <= existing_max:
                raise ValueError(
                    f"New data starts at {new_min}, which is not strictly after the store's "
                    f"latest timestamp ({existing_max}). Appends must be chronological -- "
                    "backfilling an earlier gap needs a separate process."
                )

        ds.to_zarr(path, mode="a", append_dim=TIME_DIM, consolidated=True)
        print(f"  appended {ds.sizes[TIME_DIM]} time step(s) to existing store at {path}")

    return xr.open_zarr(path)


def main() -> None:
    args = parse_args()
    timestamps = hourly_timestamps(args.start, args.end)

    print(f"Loading {len(timestamps)} hourly time step(s) from ARCO-ERA5 ...")
    mslp = load_arco_mslp(timestamps, THIN_STEP)
    print(f"  mslp shape: {dict(mslp.sizes)}")

    print("Computing 11-type circulation types ...")
    cts_11 = compute_cts11(mslp)

    ds = build_dataset(cts_11)

    print(f"Writing to {OUTPUT_PATH} ...")
    result = write_or_append(ds, OUTPUT_PATH)

    size_bytes = sum(f.stat().st_size for f in OUTPUT_PATH.rglob("*") if f.is_file())
    print(
        f"Done. {OUTPUT_PATH} now covers {result.sizes[TIME_DIM]} time step(s) "
        f"[{pd.Timestamp(result[TIME_DIM].values.min())} .. "
        f"{pd.Timestamp(result[TIME_DIM].values.max())}] ({size_bytes / 1e3:.1f} KB)"
    )


if __name__ == "__main__":
    main()
