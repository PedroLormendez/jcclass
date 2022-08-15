# Jenkinson - Collison automated gridded classification for Python
This is an adapted version for python of the __Jenkinson - Collison__ automated classfication based on the original Lamb Weather Types. This gridded version is based on the application made by [Otero](https://link.springer.com/article/10.1007/s00382-017-3705-y) (2018) using a moving central gridded point with  that allows to compute the synoptic circulation types on a gridded Mean Sea Level Pressure (MSLP) domain.
![](https://github.com/PedroLormendez/JC-Classification/blob/main/figs/Circulations_quick.gif)
## How does it work?
The method uses grid-point MSLP data to obtain numerical values of wind flow and vorticity which can be used to determine Cyclonic and Anticyclonic patterns as well as their dominant advective (direction of wind flow) characteristics. The 16 gridded points are moved along the region in reference to a central point where the dominant circulation type will be designated.   
![](https://github.com/PedroLormendez/JK-Classification-Beta/blob/main/figs/Gridpoints.gif)
## Method and equations
- __Westerly flow__


$W = \frac{1}{2}(P_12 + P_13) -  \frac{1}{2}(P_4 + P5)$

- __Southerly flow__

$S = sc[\frac{1}{4}(P_5 + 2P_9 + P_{13}) - \frac{1}{4}(P_4 + 2P_8 + P_{12})]$

- __Resultant flow__

$F = \sqrt{S^2 + W^2}$

- __Westerly shear vorticity__

$ZW = zwb[\frac{1}{2}(P_{15} + P_{16}) - \frac{1}{2}(P_8 + P_9)] - zsc[\frac{1}{2}(P_8 + P_9) - \frac{1}{2}(P_1 + P_2)]$

- __Southerly shear vorticity__

$ZS = zwa[\frac{1}{4}(P_6 + 2P_{10} + P_{14}) - \frac{1}{4}(P_5 + 2P_9 + P_{13}) -\frac{1}{4}(P_4 + 2P_8 + P_{12}) + \frac{1}{4}(P_3 + 2P_7 + P_{11}]$

- __Total shear vorticity__

$Z = ZW + ZS$

The flow units are geostrophic, expressed as hPa per 10º latitude; each unit is equivalent to 1.2 knots (0.6 m/s). The geostrophic units are expressed as hPa per 10º latitude; 100 units are equivalent to $0.55 x 10^{-4} = 0.46$ time the Coriolis parameter.

The latitude dependant constants account for the relative differences between the grid-point spacing in the east-west and north-south direction and are defined as follows (being $\phi$ the latitude of the central point):

$sc = \frac{1}{\cos{\phi}} $

$zwa = \frac{\sin{\phi}}{\sin{\phi - 5}}$

$zwb = \frac{\sin{}\phi}{\sin{\phi + 5}}$

$zsc = \frac{1}{2(\cos^2{\phi})}$

The rules to define the appropiate Circulation Type (Lamb weather type) are:

1. The direction of flow is $\tan^{-1}{(W/S)}$. Add 180º if $W$ is positive. The appropiate direction is calculated on an eight-point compass allowing 45º per sector. Thus $W$ occurs between 247.5º and 292.5º

2. If $|Z| < F$, flow is essentially straight and corresponds to a Lamb pure directional type (NE, E, SE, S, etc).

3. If $|Z| > 2F$, then the pattern is strongly cyclonic $(Z>0)$ or anticyclonic $(Z<0)$. This corresponds to a Lamb's pure cyclonic and anticyclonic type (A or C).

4. If $|Z|$ lies between $F$ and $2F$ ($F < |Z| < 2F$) then the flow is partly (anti)-cyclonic. The flow is considered a hybrid type and is therefore characterised by both direction and circulation (ANE, AE, ASE, ...., AN and CNE, CE, CSE, ..., CN)

5. If $F < 6$ and $|Z| < 6$, there is light indeterminate flow, corresponding to Lamb's unclassified type, represented here as Low Flow type (LF).

Detailed method in [Jones et al, 1993](https://rmets.onlinelibrary.wiley.com/doi/10.1002/joc.3370130606)

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

A sample dataset from ERA5 is provided and available [here](https://github.com/PedroLormendez/JC-Classification/tree/main/sample_data)
## Installation
Simply run in the terminal
```
pip install -i https://test.pypi.org/simple/ jc-classification
```

## How to use?
Importing the module
```py
from jc_class import jc_class
```
Starting the module.
Sample dataset available [here](https://github.com/PedroLormendez/JC-Classification/tree/main/sample_data).
```py
jc = jc_class('filename.nc')
```
- Computing the automated circulation types based on gridded MSLP
```py
cts_27 = jc.classification()
```
Computing the reduced eleven circulation types
```py
cts_11 = jc.eleven_cts(cts_27)
```
Ploting the circulation types on a map
```py
import xarray as xr
cts = cts_27.sel(time = date)
fig = jc.plot_cts(cts, *args)
```
*cts: a 2D['lat','lon']  DataArray of the 27 CTs*  
** *args (lat_south=-80, lat_north=80, lon_west=-180, lon_east=180)*
![](https://github.com/PedroLormendez/JC-Classification/blob/main/figs/plot_cts.png)

Plotting the circulation types and MSLP contour lines on a map
```py
import xarray as xr
cts = cts_27.sel(time = date)
mslp = xr.open_dataset(jc.filename).sel(time = date)

fig = jc.plot_cts_mslp(cts, mslp, *args)
```
*cts: a 2D['lat','lon']  DataArray of the 27 CTs*  
*mslp: a 2D['lat','lon'] DataArray of MSLP*  
** *args (lat_south=-80, lat_north=80, lon_west=-180, lon_east=180)*  
![](https://github.com/PedroLormendez/JC-Classification/blob/main/figs/plot_cts_mslp.png)

Plotting the circulation types and MSLP contour lines on a Nearside perspective cartopy projection
```py
import xarray as xr
cts = cts_27.sel(time = date)
mslp = xr.open_dataset(jc.filename).sel(time = date)

fig = jc.plot_cts_globe(cts, mslp, *args)
```
*cts: a 2D['lat','lon']  DataArray of the 27 CTs*  
*mslp: a 2D['lat','lon'] DataArray of MSLP*  
** *args (lat_central=30, lon_central=0)*  
![](https://github.com/PedroLormendez/JC-Classification/blob/main/figs/plot_cts_globe.png)


## Acknowledging this work
The code can be used and modified freely without any restriction. If you use it for your own research, I would appreciate if you cite this work as follows:

Herrera-Lormendez, 2022.....

Reports on errors are welcomed by [raising an issue](https://github.com/PedroLormendez/JC-Classification/issues)

## Further information on the method
- Jenkinson AF, Collison FP. 1977. An Initial Climatology of Gales over the North Sea. Synoptic Climatology Branch Memorandum, No. 62., Meteorological Office, Bracknell.
- Lamb HH. 1972. British Isles weather types and a register of daily sequence of circulation patterns, 1861-1971: Geophysical Memoir. HMSO.
- Jones PD, Hulme M, Briffa KR. 1993. A comparison of Lamb circulation types with an objective classification scheme. International Journal of Climatology. John Wiley & Sons, Ltd, 13(6): 655–663. https://doi.org/10.1002/joc.3370130606.
- Otero N, Sillmann J, Butler T. 2018. Assessment of an extended version of the Jenkinson–Collison classification on CMIP5 models over Europe. Climate Dynamics. Springer Verlag, 50(5–6): 1559–1579. https://doi.org/10.1007/s00382-017-3705-y.
