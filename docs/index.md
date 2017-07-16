---
layout: default
---

<!-- Text can be **bold**, _italic_, or ~~strikethrough~~. -->

<!-- [Link to another page](another-page). -->

<!-- There should be whitespace between paragraphs. -->

<!-- There should be whitespace between paragraphs. We recommend including a README, or a file with information about your project. -->


{% for js in page.customjs %}
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-80874546-2', 'auto');
  ga('send', 'pageview');

</script>
{% endfor %}

## [](#header-1)WeFacts

wefacts (weather-facts) makes it easy for researchers and developers to obtain historical weather data
including temperature, wind speed, wind direction, etc.


<!-- ## Data Request by Mail

Send an email to _histwx@gmail.com_ with the subject indicating the location and dates, separated by semicolon (;).  

Examples of email subjects (corresponding data available in Data Samples):

* 5000 Forbes Ave, Pittsburgh, PA 15213; 20160112; 20160112
* 15213; 20160215; 20160314
* Moffett Field, CA; 20170110; 20170123

The dates (format yyyymmdd) are the local time for the address.

wefacts will geo-locate the address, search its nearby weather stations and local severe weather reports, and then send the integrated weather data back to you.

wefacts currently supports United States addresses; the hourly weather recordings start in 1901 (though only a few stations go back that far); the PLSR severe weather reports are available since 2005.

_The email protocol is currently in its beta version. Currently the email protocol can respond all the requests within 24 hours.
If you haven't received response within 24 hours, please contact us with "help" in the email subject.
Please contact us if you need an instantaneous response - we are deciding whether to upgrade the server for real time operation._ -->

## Weather Data Source:
The Integrated Surface Hourly Data Base
in data access category Land-Based Station [https://www.ncdc.noaa.gov/data-access/land-based-station-data](https://www.ncdc.noaa.gov/data-access/land-based-station-data)
by NOAA (National Oceanic and Atmospheric Administration, [https://www.ncdc.noaa.gov/data-access](https://www.ncdc.noaa.gov/data-access)).

Specifically, the raw weather data records are available at [ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/](ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/) .
It contains hourly weather recordings from 1700+ weather stations covering every state in the US.
It also offers weather recordings for other countries with a limited coverage.

The severe weather reports, which are available at [ftp://ftp.ncdc.noaa.gov/pub/data/swdi/database-csv/v2/](ftp://ftp.ncdc.noaa.gov/pub/data/swdi/database-csv/v2/),
are also integrated into the data set.

## Hourly Weather Records Columns:
- ZTime:
- Time: local time
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

## Severe Weather Category
    - 'nx3tvs'       - (Point)   NEXRAD Level-3 Tornado Vortex Signatures
    - 'nx3meso'      - (Point)   NEXRAD Level-3 Mesocyclone Signatures
    - 'nx3hail'      - (Point)   NEXRAD Level-3 Hail Signatures
    - 'nx3structure' - (Point)   NEXRAD Level-3 Storm Cell Structure Information
    - 'plsr'         - (Point)   Preliminary Local Storm Reports
    - 'warn'         - (Polygon) Severe Thunderstorm, Tornado, Flash Flood and Special Marine warnings
    - 'nldn'         - (Point)   Lightning strikes from Vaisala (.gov and .mil ONLY)

## Missing Records

Not all weather data are recorded and missing values are represented as -9999.

## Help

If help is needed, please join our discussions on [WeFacts Google Group](https://groups.google.com/forum/#!forum/wefacts-users) 