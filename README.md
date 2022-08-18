# Jenkinson - Collison automated gridded classification for Python
This is an adapted version for python of the __Jenkinson - Collison__ automated classfication based on the original Lamb Weather Types. This gridded version is based on the application made by [Otero](https://link.springer.com/article/10.1007/s00382-017-3705-y) (2018) using a moving central gridded point with  that allows to compute the synoptic circulation types on a gridded Mean Sea Level Pressure (MSLP) domain.
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/Circulations_quick.gif)
## How does it work?
The method uses grid-point MSLP data to obtain numerical values of wind flow and vorticity which can be used to determine Cyclonic and Anticyclonic patterns as well as their dominant advective (direction of wind flow) characteristics. The 16 gridded points are moved along the region in reference to a central point where the dominant circulation type will be designated.   
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/Gridpoints.gif)

## The Circulation Types (CTs)
The application of the automated classification allows to derive 27 synoptic circulations. 26 of them based on the dominant pressure pattern and wind direction plus a Low Flow (LF) type which is characterised by days when pressure gradients are to weak and a dominant circulation or advective direction can not be assigned.

|__Name__ | __Abreviation__| __Coding__|__Name__| __Abreviation__| __Coding__|__Name__| __Abreviation__| __Coding__|
| :-      | :-:            | :-:       | :-     | :-:            | :-:       | :-     | :-:            | :-:    
|Low Flow                   | LF             | -1        
|Anticyclonic               | A              | 0         |             |   |   |Cyclonic              | C              | 20
|Anticyclonic Northeasterly | ANE            | 1         |Northeasterly| NE| 11|Cyclonic Northeasterly| CNE            | 21
|Anticyclonic Easterly      | AE             | 2         |Easterly     | E | 12|Cyclonic Easterly     | CE             | 22
|Anticyclonic Southeasterly | ASE            | 3         |Southeasterly| SE| 13|Cyclonic Southeasterly| CSE            | 23
|Anticyclonic Southerly     | AS             | 4         |Southerly    | S | 14|Cyclonic Southerly    | CS             | 24
|Anticyclonic Southwesterly | ASW            | 5         |Southwesterly| SW| 15|Cyclonic Southwesterly| CSW            | 25
|Anticyclonic Westerly      | AW             | 6         |Westerly     | W | 16|Cyclonic Westerly     | CW             | 26
|Anticyclonic Northwesterly | ANW            | 7         |Northwesterly| NW| 17|Cyclonic Northwesterly| CNW            | 27
|Anticyclonic Northerly     | AN             | 8         |Northerly    | N | 18|Cyclonic Northerly    | CN             | 28

The original 27 circulations can be reduced to a set of 11 patterns based on their dominant advection.

|Name                   | Abreviation | Coding
| :-                   | :-:          | :-:    
|Low Flow               | LF          | -1     
|Anticyclonic           | A           | 0
|Northeasterly          | NE          | 1
|Easterly               | E           | 2
|Southeasterly          | SE          | 3
|Southerly              | S           | 4
|Southwesterly          | SW          | 5
|Westerly               | W           | 6
|Northwesterly          | NW          | 7
|Northerly              | N           | 8
|Cyclonic               | C           | 9

## Working datasets

The current code has been has been tested for the following datasets:
- [ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) Reanalysis
-[NOAA](https://psl.noaa.gov/data/gridded/data.20thC_ReanV3.html) 20th Century Reanalysis (V3)
- Global Climate Models from the Coupled Model Intercomparison Project ([CMIP6](https://esgf-node.llnl.gov/projects/cmip6/))

The method can be applied for any other netcdf files with latitude coordinates names as "latitude" or "lat", or longitudes coordinates as "longitude" or "lon" and MSLP coordinate names as "msl" or "psl".

Sample datasets from ERA5 is provided and available [here](https://github.com/PedroLormendez/jc_module/tree/main/sample_data)
## Installation
Simply run in the terminal
```
pip install -i https://test.pypi.org/simple/ jcclass
```

## How to use?
__Importing the module__
```py
from jcclass import jc
```

__Computing the automated circulation types based on gridded MSLP__

Sample datasets available [here](https://github.com/PedroLormendez/jc_module/tree/main/sample_data).

```py
filename = 'era5_daily_lowres.nc'
cts_27 = jc(filename).classification()
```
__Computing the reduced eleven circulation types__
```py
cts_11 = jc.eleven_cts(cts_27)
```
__Ploting the circulation types on a map__
```py
import xarray as xr
date = cts_27.time[0] #selecting the first time
cts = cts_27.sel(time = date)
fig = jc.plot_cts(cts, *args)
```
- *cts   : a 2D['lat','lon']  xarray.DataArray of the 27 CTs*
- **args : int, __optional__ (lat_south, lat_north, lon_west, lon_east)*
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/plot_cts.png)

__Plotting the circulation types and MSLP contour lines on a map__
```py
import xarray as xr
mslp = xr.open_dataset(filename).sel(time = date)
fig = jc.plot_cts_mslp(cts, mslp, *args)
```
- *cts   : a 2D['lat','lon']  xarray.DataArray of the 27 CTs*  
- *mslp  : a 2D['lat','lon'] xarray.Dataset of MSLP*  
- **args : int, __optional__ (lat_south, lat_north, lon_west, lon_east)*  
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/plot_cts_mslp.png)

__Plotting the circulation types and MSLP contour lines on a Nearside perspective cartopy projection__
```py
fig = jc.plot_cts_globe(cts, mslp, *argsglobe)
```
- *cts   : a 2D['lat','lon']  xarray.DataArray of the 27 CTs*
- *mslp  : a 2D['lat','lon'] xarray.Dataset of MSLP*  
- **argsglobe : int, __optional__ (lat_central=30, lon_central=0)*  
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/plot_cts_globe.png)

__Saving the figures__

You can save anytime any of the figures using ``fig.savefig``.

```py
fig.savefig('figname.png', dpi = 150)
```
## Documentation

Detailed documentation and tutorial on the ``jcclass`` module can be found in the [Documentation](https://pedrolormendez-jcclass.readthedocs.io/en/latest/index.html)

## Acknowledging this work
The code can be used and modified freely without any restriction. If you use it for your own research, I would appreciate if you cite this work as follows:

Herrera-Lormendez, 2022.....

Reports on errors are welcomed by [raising an issue](https://github.com/PedroLormendez/JC-Classification/issues)

## Further literature on the method
- Jenkinson AF, Collison FP. 1977. An Initial Climatology of Gales over the North Sea. Synoptic Climatology Branch Memorandum, No. 62., Meteorological Office, Bracknell.
- Lamb HH. 1972. British Isles weather types and a register of daily sequence of circulation patterns, 1861-1971: Geophysical Memoir. HMSO.
- Jones PD, Hulme M, Briffa KR. 1993. A comparison of Lamb circulation types with an objective classification scheme. International Journal of Climatology. John Wiley & Sons, Ltd, 13(6): 655–663. https://doi.org/10.1002/joc.3370130606.
- Otero N, Sillmann J, Butler T. 2018. Assessment of an extended version of the Jenkinson–Collison classification on CMIP5 models over Europe. Climate Dynamics. Springer Verlag, 50(5–6): 1559–1579. https://doi.org/10.1007/s00382-017-3705-y.
