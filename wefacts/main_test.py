import logging
from ftplib import FTP

import matplotlib.pyplot as plt

import fetch
import match
import parse

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


def get_weather(zip_code, country, state, time_start, time_end):
    id2loc = match.match_isd_zip(zip_code, country, state, time_end)

    year_start, year_end = time_start/10000, time_end/10000
    for year in xrange(year_start, year_end+1):
        for usaf_wban, location in id2loc.items():
            if not fetch.fetch_isd_lite(year, usaf_wban):
                logger.error('cannot find %s-%d miles:%d' % (usaf_wban, year, location[0]))
                continue
            logger.info('parsed %s-%d miles:%d' % (usaf_wban, year, location[0]))
            # todo testing m1,d1,m2,d2
            m1, d1, m2, d2 = 1, 1, 12, 31
            if year*10000 < time_start:
                m1, d1 = (time_start/100) % 100, time_start % 100
            if (year+1)*10000 > time_end:
                m2, d2 = (time_end/100) % 100, time_end % 100
            df = parse.parse(usaf_wban, year, m1, d1, m2, d2)
            df.to_csv('temp.csv', index=False)
            for label in ['OAT', 'WS', 'PPT']:
                values = df[label].values
                _plot_weather(values, time_start, time_end, label=label)
            break
        else:
            logger.error('no weather info for %s in %d' % (zip_code, year))


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
    df_isd = match.load_isd(country='US')
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
    get_weather('94014', 'US', 'CA', 20170209, 20170212)
    # get_weather('15217', 'US', 'PA', 20170209, 20170214)
    # test_cmp_stations()

    # todo compare station ids between ftp-site and isd-history
    # todo what if missing values for some station -9999 : rely on interpolation or nearby stations?
    # todo decode parse the ish format (full weather record)