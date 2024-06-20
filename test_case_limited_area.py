import xarray as xr
from jcclass import jc

min_lon, max_lon, min_lat, max_lat = (4, 32, 54, 72)  # nordic

da = xr.open_dataset("sample_data/era5_hourly_highres.nc")

print(da.coords)

# Subset on limited area 'nordic'
da_subset = da.where(
    (da.longitude >= min_lon) & (da.longitude <= max_lon) & (da.latitude >= min_lat) & (da.latitude <= max_lat),
    drop=True,
)

print(da_subset.coords)

# Original test data
jc_res = jc(da)
cts_27 = jc_res.classification()
cts_11 = jc_res.eleven_cts(cts_27)

# Limited area 'nordic' test data
jc_res_nordic = jc(da_subset)
cts_27 = jc_res_nordic.classification()
cts_11 = jc_res_nordic.eleven_cts(cts_27)
