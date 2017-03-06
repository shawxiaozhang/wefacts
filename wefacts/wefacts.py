"""
Provide weather facts for a specified address and time range.
"""

import os
import datetime

import fetcher
import stations
import parser
import geo
from util import logger


def get_weather(address, date_start, date_end, dump_csv=False, result_dir='../result/',
                station_num=5, radius_miles=15, station_option='usaf_wban'):
    gps, country, state = geo.geo_address(address)
    if not gps:
        return None

    station2location = stations.search_stations(gps, country, state, date_end, station_num, radius_miles)

    if station_option is not None:
        # re-sort: prioritize high quality stations
        for usaf_wban, location in station2location.items():
            usaf, wban = usaf_wban.split('-')
            if station_option == 'usaf_wban' and (usaf == '999999' or wban == '99999') \
                    or station_option == 'usaf' and usaf == '999999' \
                    or station_option == 'wban' and wban == '99999':
                station2location.pop(usaf_wban)
                station2location[usaf_wban] = location
    logger.debug('searched stations nearby:')
    for msg in ['%s: %d miles, GPS (%.2f, %.2f), %s' % (x, v[0], v[1], v[2], v[3])for x, v in station2location.items()]:
        logger.debug(msg)

    year_start, year_end = date_start / 10000, date_end / 10000
    df, info = None, {'Address': address}
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
            info['StationID'] = usaf_wban
            info['StationName'] = location[3]
            break
        else:
            logger.error('no weather info for %s in %d' % (address, year))

    if dump_csv and df is not None:
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        df.to_csv('%s%s-%d-%d.csv' % (result_dir, address, date_start, date_end), index=False)
        logger.info('weather available : %s%s-%d-%d.csv' % (result_dir, address, date_start, date_end))

    df.info = info

    return df


def summarize_daily(df_weather):
    _remove_nan = lambda xx: [x for x in xx if (x != -9999 and x == x)]
    reports = []
    for i in xrange(0, len(df_weather), 24):
        df_daily = df_weather.iloc[i:i+24]
        dates, hours, oat, wd, ws, sky, ppt, ppt6 = df_daily['Date'].values, \
            df_daily['Hour'].values, df_daily['OAT'].values, df_daily['WD'].values, \
            df_daily['WS'].values, df_daily['SKY'].values, df_daily['PPT'].values, df_daily['PPT6'].values
        if len(_remove_nan(dates)) < len(dates)/2 or len(_remove_nan(hours)) < len(hours)/2:
            continue
        day = [d for d in dates if d != -9999 and d == d][0]
        day = datetime.datetime.strptime(str(day), '%Y%m%d').strftime('%y/%m/%d %a')
        oat = [int(round(t/10.0*1.8 + 32)) if (t == t and t != -9999) else -9999 for t in oat]
        sky = [s if s == s else -9999 for s in sky]
        sky = [s if s <= 10 else s-10 for s in sky]
        ws = [int(round(w/10*2.23694)) if (w == w and w != -9999) else -9999 for w in ws]
        ppt = [r/10.0 if (r == r and r != -9999) else -9999 for r in ppt]       # in mm
        ppt6 = [r/10.0 if (r == r and r != -9999) else -9999 for r in ppt6]     # in mm

        # todo rules to summarize daily report
        msg = 'Sunny'
        rain_sum = max(sum(_remove_nan(ppt)), sum(_remove_nan(ppt6)))
        if rain_sum >= 10.0:
            msg = 'Rainy'
            rain_hours = set()
            for h in xrange(1, 24):
                if ppt6[h] >= 1:
                    rain_hours |= set(range(h-6, h+1))
            if len(rain_hours) > 0:
                temperatures = [oat[h] for h in rain_hours]
                if sum(temperatures)*1.0/len(temperatures) < 32:
                    msg = 'Snow'
        elif sum([1 for w in ws if w > 20]) >= 5:
            msg = 'Windy'
        elif sum([1 for s in sky if s >= 6]) >= 0.5*len(_remove_nan(sky)):
            msg = 'Cloudy'
        elif sum([1 for s in sky if 3 <= s <= 6]) >= 0.5*len(_remove_nan(sky)):
            msg = 'Partly Cloudy'
        elif sum([1 for s in sky if 2 <= s <= 3]) >= 0.5*len(_remove_nan(sky)):
            msg = 'Mostly Sunny'
        oat_valid = _remove_nan(oat)
        if len(oat_valid) <= 0:
            logger.error('No OAT ' + ';'.join('%s:%s' % (k, v) for k, v in df_weather.info.items()))
            oat_valid = [-9999]
        summary = {'Low': min(oat_valid), 'High': max(oat_valid), 'MSG': msg}
        reports.append((day, summary))
    return reports