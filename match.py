import bisect
import datetime
import os
from ftplib import FTP
import logging
import urllib
import zipfile
import collections

import pandas as pd
import numpy as np
import gmplot
import Geohash
from geopy.distance import vincenty


logging.basicConfig(level=logging.DEBUG, format='%(pathname)s:%(lineno)d %(message)s',)
logger = logging.getLogger(__name__)
np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_rows', 500)


FILE_ISD = 'db/isd-history.csv'
FILE_ZIP_FMT = 'db/%4d_Gaz_zcta_national.txt'


def load_isd(country='US', state=None, time_end=None):
    time_alive = int((datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y%m%d'))
    if time_end and time_end <= time_alive:
        time_alive = time_end

    # if need to download FILE_ISD
    file_time = 0 if not os.path.isfile(FILE_ISD) \
        else int(datetime.datetime.fromtimestamp(os.path.getmtime(FILE_ISD)).strftime('%Y%m%d'))
    if time_end > file_time:
        logger.info('downloading weather stations information ...')
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/noaa/')
        ftp.retrbinary('RETR isd-history.csv', open('db/isd-history.csv', 'wb').write)
        ftp.quit()

    df = pd.read_csv(FILE_ISD)
    i_alive = df['END'] >= time_alive
    i_ctry = df['CTRY'] == country if country else True
    i_state = df['STATE'] == state if state else True
    df_isd = df.loc[i_alive & i_ctry & i_state]

    return df_isd


def load_zip_code(census_year=2016):
    file_zip = FILE_ZIP_FMT % census_year
    if not os.path.isfile(file_zip):
        file_zip_url = 'http://www2.census.gov/geo/docs/maps-data/data/gazetteer' \
                       '/%4d_Gazetteer/%4d_Gaz_zcta_national.zip' % (census_year, census_year)
        urllib.urlretrieve(file_zip_url, 'db/temp_zip_code.zip')
        zip_ref = zipfile.ZipFile('db/temp_zip_code.zip', 'r')
        zip_ref.extractall('db')
        zip_ref.close()
        os.remove('db/temp_zip_code.zip')
    zip2gps = dict()
    with open(file_zip, 'r') as f:
        for line in f.readlines()[1:]:
            fields = line.split()
            zip_code, lat, lng = fields[0], float(fields[5]), float(fields[6])
            zip2gps[zip_code] = (lat, lng)
        f.close()
    return zip2gps


def _match_gps_isd(gps, df_isd, isd_num=3):
    geo2row = dict()
    for row in xrange(len(df_isd)):
        lat, lng = df_isd.iloc[row][['LAT', 'LON']]
        geo2row[Geohash.encode(lat, lng)] = (row, lat, lng)
    geo_list = sorted(geo2row.keys())

    geo_hash = Geohash.encode(gps[0], gps[1])
    pos = bisect.bisect_left(geo_list, geo_hash)
    row2distance = dict()
    for g in geo_list[max(pos-isd_num, 0):min(pos+isd_num+1, len(geo_list))]:
        row, lat, lng = geo2row[g]
        row2distance[row] = int(vincenty((lat, lng), gps).miles)
    sorted_rows = sorted(row2distance, key=row2distance.get)

    matched = collections.OrderedDict()
    for i, row in enumerate(sorted_rows):
        distance = row2distance[row]
        if i >= 1 and distance > 10:
            continue
        if len(matched) >= isd_num:
            continue
        usaf, wban, lat, lng = df_isd.iloc[row][['USAF', 'WBAN', 'LAT', 'LON']]
        matched['%d-%d' % (usaf, wban)] = distance, lat, lng
    logger.info('GPS(%.3f, %.3f) nearby station miles %s'
                % (gps[0], gps[1], ' '.join([str(matched[x][0]) for x in matched])))
    return matched


def match_isd_zip(zip_code, country='US', state='None', time_end='None', isd_num=3):
    df_isd = load_isd(country, state, time_end)
    zip2gps = load_zip_code()
    return _match_gps_isd(zip2gps[zip_code], df_isd, isd_num)


def plot_map(gps, matched, df_isd):
    g_map = gmplot.GoogleMapPlotter(gps[0], gps[1], 10)
    g_map.scatter(df_isd['LAT'].values, df_isd['LON'].values, color='cornflowerblue', size=5)
    g_map.scatter([x[1] for x in matched.values()], [x[2] for x in matched.values()], color='red', size=9)
    g_map.scatter([gps[0]], [gps[1]], color='purple', size=9)
    g_map.draw("tmp/station_map.html")


def test_match(zip_code, state):
    df_isd = load_isd('US', state)
    zip2gps = load_zip_code()
    gps = zip2gps[zip_code]
    matched = _match_gps_isd(gps, df_isd)
    plot_map(gps, matched, df_isd)


if __name__ == '__main__':
    test_match('94014', 'CA')
