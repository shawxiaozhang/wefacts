### functions to add

- clean raw data routine
- provider platform
- support time argument : and , (like Matlab arrays)

### databases to integrate


- severe weather database

handle inch " in the string, bad for read_csv

- https://www.ncdc.noaa.gov/swdiws/

- the full ish format raw data


### stations and data source to check

- 999999-23272, SF DOWNTOWN, only record precipitation?

- 994014-99999, SEATTLE, no precipitation

- 999999-94290, WSFO SEATTLE SAND POINT, cannot find

- 722874-93134, DOWNTOWN L.A./USC CAMPUS, Los Angeles, only records several hours a day

- severe weather : ftp://ftp.ncdc.noaa.gov/pub/data/swdi/KNOWN_ISSUES.txt

- ? local time in ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/

### completed
- get_weather function
- email publisher
- user only needs specify local time
- provide a full several data record, also pick the most significant one to combine with the hourly weather data