# wefacts
wefacts ia a Python 2 client for providing historical weather data.

wefacts makes it easy for researchers and developers to obtain historical weather data
including temperature, wind speed, wind direction, etc.

## weather data source:
The Integrated Surface Hourly Data Base
in data access category Land-Based Station (https://www.ncdc.noaa.gov/data-access/land-based-station-data)
by NOAA (National Oceanic and Atmospheric Administration, https://www.ncdc.noaa.gov/data-access).

Specifically, the raw weather data records are available at ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/ .

** weather records columns:
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

## get_weather examples

    >>> from wefacts import wefacts
    >>> df = wefacts.get_weather('Pittsburgh', 20161224, 20161224)
    >>> temperature_celsius = [x/10.0 for x in df['OAT'].values]
    >>> print min(temperature_celsius), max(temperature_celsius)
    2.2 7.8
    >>> temperature_fahrenheit = [int(round(x*1.8 + 32)) for x in temperature_celsius]
    >>> print min(temperature_fahrenheit), max(temperature_fahrenheit)
    36 46

