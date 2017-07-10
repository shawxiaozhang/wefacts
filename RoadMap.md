### functions to add

- some weather stations are not updated in time
    - (1) inform user about the station's latest timestamp
    - (2) give user options to choose surrounding other stations
    - (3) or, give user multiple reports with multiple stations
- clean raw data routine
- twitter handler
- support time argument : and , (like Matlab arrays)
- download all nearby station weathers, provide a list of csv for user to choose

### databases to integrate

- double check the terms in plsr database
- severe weather database

- https://www.ncdc.noaa.gov/swdiws/

- the full ish format raw data


### stations and data source to double check

- 999999-23272, SF DOWNTOWN, only record precipitation?

- 994014-99999, SEATTLE, no precipitation

- 999999-94290, WSFO SEATTLE SAND POINT, cannot find

- 722874-93134, DOWNTOWN L.A./USC CAMPUS, Los Angeles, only records several hours a day

- severe weather : ftp://ftp.ncdc.noaa.gov/pub/data/swdi/KNOWN_ISSUES.txt

- reduce google map api usage

- improve tests

### completed
- better api interfaces
- get_weather function
- email publisher
- conversion from ZTime (UTC) to local time
- integration of severe weather data (plsr)
