import logging
from ftplib import FTP
import os

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
        logger.error('Cannot geo-locate:' + address)
        return None, None, None
    fields = [x.strip() for x in location.raw['display_name'].split(',')]
    country = fields[-1]
    state = fields[-2] if not fields[-2].isdigit() else fields[-3]
    gps = (location.latitude, location.longitude)
    return gps, const_country_abbrev.get(country, None), const_us_state_abbrev.get(state, None)


def get_weather(address, time_start, time_end, result_dir='../result/'):
    if not os.path.exists('../raw'):
        os.makedirs('../raw')
    if not os.path.exists('../result'):
        os.makedirs('../result')

    gps, country, state = _geo_address(address)
    if not gps:
        return
    logger.debug('%f %f %s %s' % (gps[0], gps[1], country, state))

    id2loc = searcher.search_isd(gps, country, state, time_end)
    logger.debug(id2loc)

    year_start, year_end = time_start/10000, time_end/10000
    for year in xrange(year_start, year_end+1):
        for usaf_wban, location in id2loc.items():
            if not fetcher.fetch_isd_lite(year, usaf_wban):
                logger.error('cannot find %s-%d miles:%d' % (usaf_wban, year, location[0]))
                continue
            logger.info('parsed %s-%d miles:%d' % (usaf_wban, year, location[0]))
            # todo testing m1,d1,m2,d2
            m1, d1, m2, d2 = 1, 1, 12, 31
            if year*10000 < time_start:
                m1, d1 = (time_start/100) % 100, time_start % 100
            if (year+1)*10000 > time_end:
                m2, d2 = (time_end/100) % 100, time_end % 100
            df = parser.parse(usaf_wban, year, m1, d1, m2, d2)
            df.to_csv('%s%s-%d-%d.csv' % (result_dir, address, time_start, time_end), index=False)
            for label in ['OAT', 'WS', 'PPT']:
                values = df[label].values
                _plot_weather(values, time_start, time_end, label=label)
            break
        else:
            logger.error('no weather info for %s in %d' % (address, year))


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
    df_isd = searcher.load_isd(country='US')
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
    get_weather('daly city', 20170209, 20170214)
    # test_cmp_stations()

    # todo compare station ids between ftp-site and isd-history
    # todo what if missing values for some station -9999 : rely on interpolation or nearby stations?
    # todo decode parse the ish format (full weather record)