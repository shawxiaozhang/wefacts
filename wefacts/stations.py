"""
Weather stations: search nearby stations.
"""

import bisect
import datetime
import os
import collections
from ftplib import FTP

import pandas as pd
import Geohash
from geopy.distance import vincenty


FILE_STATIONS = '../raw/isd-history.csv'


def load_stations(country='US', state=None, weather_end_time=None):
    """
    Load weather stations in the specified region that are alive before weather_end_time.
    :param country:
    :param state:
    :param weather_end_time:
    :return df_stations:        pandas data frame
    """
    station_alive_time = int((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d'))
    if weather_end_time:
        station_alive_time = min(station_alive_time, weather_end_time)

    file_create_time = 0 if not os.path.isfile(FILE_STATIONS) \
        else int(datetime.datetime.fromtimestamp(os.path.getmtime(FILE_STATIONS)).strftime('%Y%m%d'))
    if file_create_time <= station_alive_time:
        print 'downloading weather stations updates ...'
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/noaa/')
        if not os.path.exists('../raw'):
            os.makedirs('../raw')
        ftp.retrbinary('RETR isd-history.csv', open('../raw/isd-history.csv', 'wb').write)
        ftp.quit()

    df = pd.read_csv(FILE_STATIONS)
    i_alive = df['END'] >= station_alive_time
    i_ctry = df['CTRY'] == country if country else True
    i_state = df['STATE'] == state if state else True
    df_stations = df.loc[i_alive & i_ctry & i_state]
    return df_stations


def search_stations(gps, country='US', state='None', date_end='None', station_num=5, miles_threshold=20):
    """
    Search nearby stations for a given GPS.
    :param gps:                 (lat, lng) GPS point to search stations
    :param country:             country to search
    :param state:               state to search
    :param date_end:            only search stations that are alive before date_end
    :param station_num:         number of nearby stations to return
    :param miles_threshold:     searching radius
    :return:                    OrderedDict() of station ids, ordered by distance
    """

    df_stations = load_stations(country, state, date_end)

    geo2row = dict()
    for row in xrange(len(df_stations)):
        lat, lng = df_stations.iloc[row][['LAT', 'LON']]
        geo2row[Geohash.encode(lat, lng)] = (row, lat, lng)
    geo_list = sorted(geo2row.keys())

    geo_hash = Geohash.encode(gps[0], gps[1])
    pos = bisect.bisect_left(geo_list, geo_hash)
    row2distance = dict()
    for g in geo_list[max(pos-station_num, 0):min(pos+station_num+1, len(geo_list))]:
        row, lat, lng = geo2row[g]
        row2distance[row] = int(vincenty((lat, lng), gps).miles)
    sorted_rows = sorted(row2distance, key=row2distance.get)

    stations = collections.OrderedDict()
    for i, row in enumerate(sorted_rows):
        distance = row2distance[row]
        if i >= 1 and distance > miles_threshold:
            continue
        if len(stations) >= station_num:
            continue
        usaf, wban, lat, lng, name = df_stations.iloc[row][['USAF', 'WBAN', 'LAT', 'LON', 'STATION NAME']]
        stations['%d-%d' % (usaf, wban)] = distance, lat, lng, name
    return stations
