---
layout: default
---

<!-- Text can be **bold**, _italic_, or ~~strikethrough~~. -->

<!-- [Link to another page](another-page). -->

<!-- There should be whitespace between paragraphs. -->

<!-- There should be whitespace between paragraphs. We recommend including a README, or a file with information about your project. -->

# [](#header-1)wefacts

wefacts ia a Python 2 client for providing historical weather data.

wefacts makes it easy for researchers and developers to obtain historical weather data
including temperature, wind speed, wind direction, etc.


## Data Request by Mail

Send an email to [histwx@gmail.com](histwx@gmail.com) with the subject indicating the location and dates, separated by semicolon (;).  

Subject examples:

* 5000 Forbes Ave, Pittsburgh, PA 15213; 160101; 161231
* Pittsburgh; 20170101; 20170131

wefacts will geo-locate the address, search its nearby weather stations and local severe weather reports, and then send the requested weather data back to you. 

The dates in the subject are the local time for the address.

## weather data source:
The Integrated Surface Hourly Data Base
in data access category Land-Based Station [https://www.ncdc.noaa.gov/data-access/land-based-station-data](https://www.ncdc.noaa.gov/data-access/land-based-station-data)
by NOAA (National Oceanic and Atmospheric Administration, [https://www.ncdc.noaa.gov/data-access](https://www.ncdc.noaa.gov/data-access)).

Specifically, the raw weather data records are available at [ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/](ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/) .
It contains hourly weather recordings from 1700+ weather stations covering every state in the US.
It also offers weather recordings for other countries with a limited coverage.

The severe weather reports, which are available at [ftp://ftp.ncdc.noaa.gov/pub/data/swdi/database-csv/v2/](ftp://ftp.ncdc.noaa.gov/pub/data/swdi/database-csv/v2/),
are also integrated into the data set.

## hourly weather records columns:
- OAT: outdoor air temperature (in Celsius, scaled by 10)
- DT: dew point temperature (in Celsius, scaled by 10)
- SLP: sea level pressure (in Hectopascals, scaled by 10)
- WD: wind direction (in Angular Degrees, scaled by 1)
    * clockwise direction, between true north and the direction from which the wind is blowing
    * wind direction for calm winds is coded as 0
- WS: wind speed rate (in meters per second, scaled by 10)
- PPT: liquid precipitation depth dimension for one hour (in millimeters, scaled by 10)
- PPT6: liquid precipitation depth dimension for six hour (in millimeters, scaled by 10)
- SKY: sky condition total coverage code
    * 0: None, SKC or CLR
    * 1: One okta - 1/10 or less but not zero
    * 2: Two oktas - 2/10 - 3/10, or FEW
    * 3: Three oktas - 4/10
    * 4: Four oktas - 5/10, or SCT
    * 5: Five oktas - 6/10
    * 6: Six oktas - 7/10 - 8/10
    * 7: Seven oktas - 9/10 or more but not 10/10, or BKN
    * 8: Eight oktas - 10/10, or OVC
    * 9: Sky obscured, or cloud amount cannot be estimated
    * 10: Partial obscuration
    * 11: Thin scattered
    * 12: Scattered
    * 13: Dark scattered
    * 14: Thin broken
    * 15: Broken
    * 16: Dark broken
    * 17: Thin overcast
    * 18: Overcast
    * 19: Dark overcast

## severe weather category
    - 'nx3tvs'       - (Point)   NEXRAD Level-3 Tornado Vortex Signatures
    - 'nx3meso'      - (Point)   NEXRAD Level-3 Mesocyclone Signatures
    - 'nx3hail'      - (Point)   NEXRAD Level-3 Hail Signatures
    - 'nx3structure' - (Point)   NEXRAD Level-3 Storm Cell Structure Information
    - 'plsr'         - (Point)   Preliminary Local Storm Reports
    - 'warn'         - (Polygon) Severe Thunderstorm, Tornado, Flash Flood and Special Marine warnings
    - 'nldn'         - (Point)   Lightning strikes from Vaisala (.gov and .mil ONLY)

## missing records

Not all weather data are recorded and missing values are represented as -9999.

## help

If help is needed, please send an email to [histwx@gmail.com](histwx@gmail.com) with the word "help" starting in the subject.