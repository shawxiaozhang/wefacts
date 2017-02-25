# wefacts
wefacts ia a Python 2 client for providing historical weather data.

wefacts makes it easy for researchers and developers to obtain historical weather data
including temperature, wind speed, wind direction, etc.

## weather data source:
NOAA (National Oceanic and Atmospheric Administration, http://www.noaa.gov/)
Specifically, the weather data is available from ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/

## get_weather

    >>> from wefacts import wefacts
    >>> df = wefacts.get_weather('Pittsburgh', 20161224, 20161224)
    >>> temperature_celsius = [x/10.0 for x in df['OAT'].values]
    >>> print min(temperature_celsius), max(temperature_celsius)
    2.2 7.8
