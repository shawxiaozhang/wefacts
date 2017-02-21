import logging
from ftplib import FTP
import os

import pandas as pd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

import fetcher
import searcher
import parser
from util import *

logging.basicConfig(level=logging.DEBUG, format='%(pathname)s:%(lineno)d %(message)s',)
logger = logging.getLogger(__name__)


def _plot_weather(values, time_start, time_end, label=''):
    # todo interpolation
    i = 0
    while values[i] == -9999:
        i += 1
        if i >= len(values):
            logger.error('error in weather data : all -9999')
            return
    for j in xrange(i):
        values[j] = values[i]
    while i < len(values):
        if values[i] == -9999:
            values[i] = values[i - 1]
        i += 1

    y_unit = ''
    if label == 'OAT':
        values = [x / 10.0 for x in values]
        y_unit = 'Celsius'
    elif label == 'WS':
        values = [x * 0.223694 for x in values]
        y_unit = 'mph'
    elif label == 'PPT':
        y_unit = 'mm'

    plt.figure()
    plt.plot(xrange(len(values)), values, label=label)
    plt.xticks(xrange(0, len(values), 24))
    plt.xlabel('%d - %d' % (time_start, time_end))
    plt.ylabel(y_unit)
    plt.grid()
    plt.show()


def _geo_address(address):
    geo_locator = Nominatim()
    location = geo_locator.geocode(address)
    if not location:
        logger.error('%s : cannot geo-locate.' % address)
        return None, None, None
    fields = [x.strip() for x in location.raw['display_name'].split(',')]
    country = fields[-1]
    state = fields[-2] if not fields[-2].isdigit() else fields[-3]
    gps = (location.latitude, location.longitude)
    logger.info('%s : gps(%f %f) country %s (%s) state %s (%s)'
                % (address, gps[0], gps[1], country, const_country_abbrev.get(country, None),
                   state, const_us_state_abbrev.get(state, None)))
    return gps, const_country_abbrev.get(country, None), const_us_state_abbrev.get(state, None)


def get_weather(address, time_start, time_end, dump_csv=True, result_dir='../result/'):
    gps, country, state = _geo_address(address)
    if not gps:
        return None

    station2location = searcher.search_stations(gps, country, state, time_end)

    # re-sort: prioritize high quality stations
    for usaf_wban, location in station2location.items():
        usaf, wban = usaf_wban.split('-')
        if usaf == '999999' or wban == '99999':
            station2location.pop(usaf_wban)
            station2location[usaf_wban] = location
    logger.debug('searched stations nearby:')
    for msg in ['%s: %d, (%.2f, %.2f)' % (x, v[0], v[1], v[2])for x, v in station2location.items()]:
        logger.debug(msg)

    year_start, year_end = time_start/10000, time_end/10000
    df = None
    for year in xrange(year_start, year_end+1):
        for usaf_wban, location in station2location.items():
            if not fetcher.fetch_isd_lite(year, usaf_wban):
                logger.error('cannot find %s-%d miles:%d' % (usaf_wban, year, location[0]))
                continue
            logger.info('parsed %s-%d miles:%d' % (usaf_wban, year, location[0]))
            m1, d1, m2, d2 = 1, 1, 12, 31
            if year*10000 < time_start:
                m1, d1 = (time_start/100) % 100, time_start % 100
            if (year+1)*10000 > time_end:
                m2, d2 = (time_end/100) % 100, time_end % 100
            temp = parser.parse_raw(usaf_wban, year, m1, d1, m2, d2)
            df = temp if df is None else df.append(temp)
            break
        else:
            logger.error('no weather info for %s in %d' % (address, year))

    if dump_csv and df is not None:
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        df.to_csv('%s%s-%d-%d.csv' % (result_dir, address, time_start, time_end), index=False)
        logger.info('weather available : %s%s-%d-%d.csv' % (result_dir, address, time_start, time_end))

    return df


def test_get_weather_cross_year():
    address, time_start, time_end, result_dir = 'squirrel hill', 20161224, 20170107, '../result/'
    get_weather(address, time_start, time_end, True, result_dir)
    df = pd.read_csv('%s%s-%d-%d.csv' % (result_dir, address, time_start, time_end))
    for label in ['OAT', 'WS', 'PPT']:
        values = df[label].values
        _plot_weather(values, time_start, time_end, label=label)


def test_cmp_stations():
    ftp_ids = set()
    ftp = FTP('ftp.ncdc.noaa.gov')
    ftp.login()
    ftp.cwd('pub/data/noaa/isd-lite/%d' % 2017)
    # ftp.cwd('pub/data/noaa/%d' % 2017)
    for f in ftp.nlst():
        usaf, wban, suffix = str(f).split('-')
        ftp_ids.add(usaf + '-' + wban)
    ftp.quit()

    found, miss = set(), set()
    df_isd = searcher.load_stations(country='US')
    for i in xrange(len(df_isd)):
        usaf, wban = df_isd.iloc[i][['USAF', 'WBAN']]
        name = '%6d-%05d' % (usaf, wban)
        if name in ftp_ids:
            found.add(name)
        else:
            miss.add(name)
    print len(ftp_ids), len(df_isd)
    print len(found), len(miss), 1.0*len(miss)/(len(found)+len(miss))
    print 'found', found
    print 'miss', miss


if __name__ == '__main__':
    # test_cmp_stations()
    # test_get_weather_cross_year()
    # get_weather_csv('220 macdonald ave', 20170209, 20170216)
    get_weather('daly city', 20170219, 20170222)

    # todo station quality analysis => every 3 hours? no rain?
    # todo how to choose the best station? (precision, no rain data, no wind data)
    # log output stating all possible stations, then let the users decide which one to use.

    # todo decode parse the ish format (full weather record)
