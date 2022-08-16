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
from jcclass import jcclass
```
__Starting the module__  
Sample datasets available [here](https://github.com/PedroLormendez/jc_module/tree/main/sample_data).
```py
jc = jcclass('filename.nc')
```
__Computing the automated circulation types based on gridded MSLP__
```py
cts_27 = jc.classification()
```
__Computing the reduced eleven circulation types__
```py
cts_11 = jc.eleven_cts(cts_27)
```
__Ploting the circulation types on a map__
```py
import xarray as xr
cts = cts_27.sel(time = date)
fig = jc.plot_cts(cts, *args)
```
- *cts   : a 2D['lat','lon']  DataArray of the 27 CTs*
- **args : (lat_south, lat_north, lon_west, lon_east)*
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/plot_cts.png)

__Plotting the circulation types and MSLP contour lines on a map__
```py
import xarray as xr
cts = cts_27.sel(time = date)
mslp = xr.open_dataset(jc.filename).sel(time = date)

fig = jc.plot_cts_mslp(cts, mslp, *args)
```
- *cts   : a 2D['lat','lon']  DataArray of the 27 CTs*  
- *mslp  : a 2D['lat','lon'] DataArray of MSLP*  
- **args : (lat_south, lat_north, lon_west, lon_east)*  
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/plot_cts_mslp.png)

__Plotting the circulation types and MSLP contour lines on a Nearside perspective cartopy projection__
```py
import xarray as xr
cts = cts_27.sel(time = date)
mslp = xr.open_dataset(jc.filename).sel(time = date)

fig = jc.plot_cts_globe(cts, mslp, *args)
```
- *cts   : a 2D['lat','lon']  DataArray of the 27 CTs*
- *mslp  : a 2D['lat','lon'] DataArray of MSLP*  
- **args : (lat_central, lon_central)*  
![](https://github.com/PedroLormendez/jc_module/blob/main/figs/plot_cts_globe.png)


## Acknowledging this work
The code can be used and modified freely without any restriction. If you use it for your own research, I would appreciate if you cite this work as follows:

Herrera-Lormendez, 2022.....

Reports on errors are welcomed by [raising an issue](https://github.com/PedroLormendez/JC-Classification/issues)