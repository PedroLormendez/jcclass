# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [v0.0.12] - 2026-08-27
### Fixed
- `compute_cts()` almost never assigned the Low Flow (LF) type on standard ERA5-scale (Pascal) input. MSLP in Pa is ~100x larger than the hPa values the Low Flow rule (`F < 6` and `|Z| < 6`) is calibrated for, so those absolute thresholds were essentially never satisfied — every other circulation type is a *ratio* between `F` and `Z` and so was unaffected by the uniform scale error, but LF was silently near-zero regardless of actual weather. Added `standardize_mslp_units()`, which detects Pa-scale input by magnitude (sea-level pressure is always ~85000-110000 Pa or ~850-1100 hPa, so the two never overlap) and converts to hPa before classification. This is also what `compute_cts()`'s docstring already documented as accepted input ("Should be in Pascals (Pa) or Hectopascals (hPa)") but never actually implemented. On a January 1979 sample, LF share went from ~0% to ~18% of classifications.

## [v0.0.11] - 2026-08-11
### Fixed
- Published package (wheel and sdist) no longer bundles unrelated repository content. Missing package-discovery restrictions and no `MANIFEST.in` meant `sample_data/`, `notebooks/`, and `figs/` were being swept into every release — the wheel was 36MB and included two ERA5 sample netCDFs, both tutorial notebooks, and two gifs. Added `MANIFEST.in` and restricted `[tool.setuptools.packages.find]` to `jcclass*`; wheel and sdist are now ~24KB each.

## [v0.0.10] - 2026-06-14
### Fixed
- Plotting with custom area (`lat_south`, `lat_north`, etc.) no longer crashes on shapely 2.x / Python 3.11.
- Axis tick labels now use cartopy's `set_xticks`/`set_yticks` instead of the gridliner, fixing compatibility with newer cartopy versions.

### Added
- Progress bar (via `tqdm`) shown during `jc_classification()` computation.
- `tqdm` added as a package dependency.

### Changed
- Logging follows library best practices — `NullHandler` by default, no console output unless the user configures it.

## [v0.0.9] - 2025-04-09
### Changed
- Package metadata now includes the full README as the long description, improving the PyPI project page.

## [v0.0.8] - 2025-04-09
### Fixed
- Versioning configuration consolidated into `pyproject.toml`, removing the need for a separate `setup.py`.

## [v0.0.7] - 2025-04-08
### Added
- Support for `xarray.Dataset` and `xarray.DataArray` as inputs (previously only one was accepted).
- Support for limited-area (non-global) domains: longitude slicing replaced with `xr.where` to correctly handle regional grids.

### Changed
- Improved module structure and internal organisation.

### Removed
- Read the Docs configuration and docs folder (documentation removed from the repo).

## [v0.0.4] - 2023-10-11
### Fixed
- Corrected `is_world()` function to properly detect global vs. regional grids.

## [v0.0.3] - 2022-09-19
### Fixed
- Fixed MSLP input handling issue.

### Added
- Citation information added to the repository.

## [v0.0.2] - 2022
### Added
- Initial public release on PyPI.
