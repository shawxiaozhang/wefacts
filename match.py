import bisect
import datetime
import os
from ftplib import FTP
import logging

import pandas as pd
import numpy as np
import gmplot
import Geohash
from geopy.distance import vincenty


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_rows', 500)


FILE_ISD = 'config/isd-history.csv'
FILE_ZIP = 'config/2016_Gaz_zcta_national.txt'

# http://www2.census.gov/geo/docs/maps-data/data/gazetteer/2016_Gazetteer/2016_Gaz_zcta_national.zip

def load_isd(end_time=None):
    if not end_time:
        end_time = int((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d'))

    # if need to download FILE_ISD
    file_time = 0 if not os.path.isfile(FILE_ISD) \
        else int(datetime.datetime.fromtimestamp(os.path.getmtime(FILE_ISD)).strftime('%Y%m%d'))
    if end_time > file_time:
        logger.info('downloading weather stations information ...')
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/noaa/')
        ftp.retrbinary('RETR isd-history.csv', open('config/isd-history.csv', 'wb').write)
        ftp.quit()

    df = pd.read_csv(FILE_ISD)
    i_alive = df['END'] >= end_time
    i_us = df['CTRY'] == 'US'
    i_state = df['STATE'] == 'CA'
    isd_select = df.loc[i_us & i_state & i_alive]
    temp = isd_select[['STATION NAME', 'CTRY', 'STATE', 'LAT', 'LON']].sort_values(by=['LON', 'LAT'], ascending=[1, 1])
    lats = temp['LAT'].values
    lngs = temp['LON'].values

    print len(isd_select)
    print temp

    plot_map(lats, lngs)
    # with open(FILE_ISD, 'r') as f:
    #     print len(f.readlines())
    #     for line in f.readlines()[:30]:
    #         print line


def load_zip_code():
    zip2gps = dict()
    with open(FILE_ZIP, 'r') as f:
        for line in f.readlines()[1:]:
            fields = line.split()
            zip_code, lat, lng = fields[0], float(fields[5]), float(fields[6])
            geo = Geohash.encode(lat, lng)
            zip2gps[zip_code] = (geo, lat, lng)
        f.close()
    return zip2gps


def plot_map(lats, lngs):
    geo2isd = dict()
    for lat, lng in zip(lats, lngs):
        geo2isd[Geohash.encode(lat, lng)] = (lat, lng)

    zip2gps = load_zip_code()
    geo, lat, lng = zip2gps['94014']

    geos = sorted(geo2isd.keys())
    idx = bisect.bisect_left(geos, geo)
    print idx
    nearby = [geo2isd[isd] for isd in geos[idx-1:idx+5]]
    nearby_lats = [x[0] for x in nearby]
    nearby_lngs = [x[1] for x in nearby]

    distances = [int(vincenty((lat, lng), x).miles) for x in nearby]
    print distances

    center_lat, center_lng = np.mean(lats), np.mean(lngs)
    g_map = gmplot.GoogleMapPlotter(center_lat, center_lng, 6)
    g_map.scatter(lats, lngs, color='cornflowerblue', size=7)
    g_map.scatter(nearby_lats, nearby_lngs, color='red', size=10)
    # g_map.heatmap(heat_lats, heat_lngs)
    g_map.draw("mymap.html")


if __name__ == '__main__':
    load_isd()
    # load_zip_code()