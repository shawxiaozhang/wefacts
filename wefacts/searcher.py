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

import util


def load_stations(dir_raw, country='US', state=None, date_weather_end=None):
    """
    Load weather stations in the specified region that are alive before weather_end_time.
    :param country:
    :param state:
    :param date_weather_end:    datetime.datetime
    :return df_stations:        pandas data frame
    """
    station_alive_time = int((datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d'))
    # todo (1) necessary to check station latest report time? (2) notify users about the latest available data
    if date_weather_end:
        station_alive_time = min(station_alive_time, int(date_weather_end.strftime('%Y%m%d')))

    if not os.path.exists(dir_raw):
        os.makedirs(dir_raw)
    stations_csv_file = '%sisd-history.csv' % dir_raw

    file_create_time = 0 if not os.path.isfile(stations_csv_file) \
        else int(datetime.datetime.fromtimestamp(os.path.getmtime(stations_csv_file)).strftime('%Y%m%d'))
    if file_create_time <= station_alive_time:
        util.logger.debug('downloading weather stations updates ...')
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/noaa/')
        ftp.retrbinary('RETR isd-history.csv', open(stations_csv_file, 'wb').write)
        ftp.quit()

    df = pd.read_csv(stations_csv_file)
    i_alive = df['END'] >= station_alive_time
    i_ctry = df['CTRY'] == country if country else True
    i_state = df['STATE'] == state if state else True
    df_stations = df.loc[i_alive & i_ctry & i_state]
    return df_stations


def search_stations(gps, dir_raw, country='US', state='None', date_end='None', station_num=5, radius_miles=15,
                    station_option='usaf_wban'):
    """
    Search nearby stations for a given GPS.
    :param gps:                 (lat, lng) GPS point to search stations
    :param country:             country to search
    :param state:               state to search
    :param date_end:            only search stations that are alive before date_end
    :param station_num:         number of nearby stations to return
    :param radius_miles:        searching radius
    :return:                    OrderedDict() of station ids, ordered by distance
    """

    df_stations = load_stations(dir_raw, country, state, date_end)

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

    station2location = collections.OrderedDict()
    for i, row in enumerate(sorted_rows):
        distance = row2distance[row]
        if i >= 1 and distance > radius_miles:
            continue
        if len(station2location) >= station_num:
            continue
        usaf, wban, lat, lng, name = df_stations.iloc[row][['USAF', 'WBAN', 'LAT', 'LON', 'STATION NAME']]
        station2location['%06d-%05d' % (usaf, wban)] = {
            'distance': distance,
            'lat': lat,
            'lng': lng,
            'name': name
        }

    if station_option is not None:
        # re-sort: prioritize high quality stations
        for usaf_wban, location in station2location.items():
            usaf, wban = usaf_wban.split('-')
            if station_option == 'usaf_wban' and (usaf == '999999' or wban == '99999') \
                    or station_option == 'usaf' and usaf == '999999' \
                    or station_option == 'wban' and wban == '99999':
                station2location.pop(usaf_wban)
                station2location[usaf_wban] = location

    return station2location
