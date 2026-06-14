# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [v0.0.10] - 2026-06-14
### Changed
- `jc_classification()` now shows a progress bar (via `tqdm`) during computation, making it easier to track progress on large datasets.
- Logging now follows library best practices: a `NullHandler` is attached by default, so no output is printed unless the user explicitly configures logging in their application.

### Added
- `tqdm` added as a package dependency.

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
