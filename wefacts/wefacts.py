"""
Provide weather facts for a specified address and time range.
"""

import os

import fetcher
import stations
import parser
import geo
from util import logger


def get_weather(address, date_start, date_end, dump_csv=False, result_dir='../result/'):
    gps, country, state = geo.geo_address(address)
    if not gps:
        return None

    station2location = stations.search_stations(gps, country, state, date_end)

    # re-sort: prioritize high quality stations
    for usaf_wban, location in station2location.items():
        usaf, wban = usaf_wban.split('-')
        if usaf == '999999' or wban == '99999':
            station2location.pop(usaf_wban)
            station2location[usaf_wban] = location
    logger.debug('searched stations nearby:')
    for msg in ['%s: %d miles, GPS (%.2f, %.2f), %s' % (x, v[0], v[1], v[2], v[3])for x, v in station2location.items()]:
        logger.debug(msg)

    year_start, year_end = date_start / 10000, date_end / 10000
    df = None
    for year in xrange(year_start, year_end+1):
        for usaf_wban, location in station2location.items():
            if not fetcher.fetch_raw_lite(year, usaf_wban):
                logger.error('cannot find %s-%d miles:%d' % (usaf_wban, year, location[0]))
                continue
            logger.info('parsed %s-%d %d miles at %s' % (usaf_wban, year, location[0], location[3]))
            m1, d1, m2, d2 = 1, 1, 12, 31
            if year*10000 < date_start:
                m1, d1 = (date_start / 100) % 100, date_start % 100
            if (year+1)*10000 > date_end:
                m2, d2 = (date_end / 100) % 100, date_end % 100
            df_temp = parser.parse_raw_lite(usaf_wban, year, m1, d1, m2, d2)
            df = df_temp if df is None else df.append(df_temp)
            break
        else:
            logger.error('no weather info for %s in %d' % (address, year))

    if dump_csv and df is not None:
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        df.to_csv('%s%s-%d-%d.csv' % (result_dir, address, date_start, date_end), index=False)
        logger.info('weather available : %s%s-%d-%d.csv' % (result_dir, address, date_start, date_end))

    return df


if __name__ == '__main__':
    get_weather('15213', 20170212, 20170219)
