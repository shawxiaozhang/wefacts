import bisect
import datetime
import os
from ftplib import FTP
import logging
import urllib
import zipfile
import collections

import pandas as pd
import gmplot
import Geohash
from geopy.distance import vincenty


logging.basicConfig(level=logging.DEBUG, format='%(pathname)s:%(lineno)d %(message)s',)
logger = logging.getLogger(__name__)
pd.set_option('display.max_rows', 500)


FILE_ISD = '../raw/isd-history.csv'
FILE_ZIP_FMT = '../raw/%4d_Gaz_zcta_national.txt'


def load_stations(country='US', state=None, weather_time_end=None):
    station_alive_time = int((datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y%m%d'))
    if weather_time_end and weather_time_end <= station_alive_time:
        station_alive_time = weather_time_end
    if not weather_time_end:
        weather_time_end = station_alive_time

    file_create_time = 0 if not os.path.isfile(FILE_ISD) \
        else int(datetime.datetime.fromtimestamp(os.path.getmtime(FILE_ISD)).strftime('%Y%m%d'))
    if weather_time_end > file_create_time:
        logger.info('downloading weather stations information ...')
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/noaa/')
        if not os.path.exists('../raw'):
            os.makedirs('../raw')
        ftp.retrbinary('RETR isd-history.csv', open('../raw/isd-history.csv', 'wb').write)
        ftp.quit()

    df = pd.read_csv(FILE_ISD)
    i_alive = df['END'] >= station_alive_time
    i_ctry = df['CTRY'] == country if country else True
    i_state = df['STATE'] == state if state else True
    df_isd = df.loc[i_alive & i_ctry & i_state]

    return df_isd


def load_zip_code(census_year=2016):
    file_zip = FILE_ZIP_FMT % census_year
    if not os.path.isfile(file_zip):
        file_zip_url = 'http://www2.census.gov/geo/docs/maps-data/data/gazetteer' \
                       '/%4d_Gazetteer/%4d_Gaz_zcta_national.zip' % (census_year, census_year)
        urllib.urlretrieve(file_zip_url, '../raw/temp_zip_code.zip')
        zip_ref = zipfile.ZipFile('../raw/temp_zip_code.zip', 'r')
        zip_ref.extractall('../raw')
        zip_ref.close()
        os.remove('../raw/temp_zip_code.zip')
    zip2gps = dict()
    with open(file_zip, 'r') as f:
        for line in f.readlines()[1:]:
            fields = line.split()
            zip_code, lat, lng = fields[0], float(fields[5]), float(fields[6])
            zip2gps[zip_code] = (lat, lng)
        f.close()
    return zip2gps


def search_stations(gps, country='US', state='None', time_end='None', station_num=5, miles_threshold=20):
    """
    search nearby stations for a given GPS.
    :param gps:                 (lat, lng) GPS point to search stations
    :param country:             country to search
    :param state:               state to search
    :param time_end:            stations should keep uploading data till this time
    :param station_num:         number of nearby stations to return
    :param miles_threshold:     searching radius
    :return:                    OrderedDict() of station ids, ordered by distance
    """

    df_isd = load_stations(country, state, time_end)

    geo2row = dict()
    for row in xrange(len(df_isd)):
        lat, lng = df_isd.iloc[row][['LAT', 'LON']]
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
        usaf, wban, lat, lng, name = df_isd.iloc[row][['USAF', 'WBAN', 'LAT', 'LON', 'STATION NAME']]
        stations['%d-%d' % (usaf, wban)] = distance, lat, lng, name
    logger.info('GPS(%.3f, %.3f) nearby station miles %s'
                % (gps[0], gps[1], ' '.join([str(stations[x][0]) for x in stations])))
    return stations


def plot_map(gps, matched, df_isd):
    g_map = gmplot.GoogleMapPlotter(gps[0], gps[1], 10)
    g_map.scatter(df_isd['LAT'].values, df_isd['LON'].values, color='cornflowerblue', size=5)
    g_map.scatter([x[1] for x in matched.values()], [x[2] for x in matched.values()], color='red', size=9)
    g_map.scatter([gps[0]], [gps[1]], color='purple', size=9)
    g_map.draw("tmp/station_map.html")


def test_match(zip_code, state):
    df_isd = load_stations('US', state)
    zip2gps = load_zip_code()
    gps = zip2gps[zip_code]
    stations = search_stations(gps, 'US', state)
    plot_map(gps, stations, df_isd)


def test_station_quality(country='US', state=None):
    df_station = load_stations(country, state)
    lats_star, lngs_star, lats_poor, lngs_poor = [], [], [], []
    for i in xrange(len(df_station)):
        usaf, wban, lat, lng = df_station.iloc[i][['USAF', 'WBAN', 'LAT', 'LON']]
        if usaf == 999999 or wban == 99999:
            lats_poor.append(lat)
            lngs_poor.append(lng)
        else:
            lats_star.append(lat)
            lngs_star.append(lng)
    g_map = gmplot.GoogleMapPlotter(1.0*sum(lats_star)/len(lats_star), 1.0*sum(lngs_star)/len(lngs_poor), 6)
    g_map.scatter(lats_star, lngs_star, color='red', size=8)
    g_map.scatter(lats_poor, lngs_poor, color='blue', size=5)
    g_map.draw('../raw/star_stations.html')


if __name__ == '__main__':
    # test_match('94014', 'CA')
    # test_station_quality(country='US', state='CO')
    test_station_quality(country='US')
