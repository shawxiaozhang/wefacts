"""
Provide weather facts for a specified address and time range.
"""

import os
import datetime
import urllib2
import json
from dateutil import tz
import collections

import pandas as pd

import fetcher
import searcher
import parser
import geo
from util import logger


def get_weather(address, date_start, date_end, dump_csv=False, result_dir='../result/',
                station_num=5, radius_miles=15, station_option='usaf_wban', severe_weather='plsr'):
    gps, country, state = geo.geo_address(address)
    if not gps:
        return None

    if isinstance(date_start, int):
        date_start = datetime.datetime.strptime(str(date_start), '%Y%m%d')
    if isinstance(date_end, int):
        date_end = datetime.datetime.strptime(str(date_end), '%Y%m%d')

    local_time_zone = tz.gettz(_get_time_zone(gps, date_start))
    date_start_utc = date_start.replace(tzinfo=local_time_zone).astimezone(tz.gettz('UTC'))
    date_end_utc = date_end.replace(tzinfo=local_time_zone).astimezone(tz.gettz('UTC'))

    station2location = searcher.search_stations(gps, country, state, date_end_utc, station_num, radius_miles, station_option)
    logger.debug('searched stations nearby:')
    for msg in ['%s: %d miles, GPS (%.2f, %.2f), %s' % (x, v[0], v[1], v[2], v[3])for x, v in station2location.items()]:
        logger.debug(msg)

    meta = {'Address': address}
    df = get_weather_lite(date_start_utc, date_end_utc, station2location)
    df.set_index('ZTime')
    meta['Stations'] = df.stations

    if severe_weather is not None:
        df_sw, df_sw_raw = get_weather_severe(severe_weather, date_start_utc, date_end_utc, gps)

        _dataframe_convert_local_time(df_sw_raw, local_time_zone)
        if dump_csv and df_sw_raw is not None:
            meta['SWFilename'] = '%s%s-%s-%s-SW.csv' % (result_dir, address, date_start.strftime('%Y%m%d'),
                                                        date_end.strftime('%Y%m%d'))
            df_sw_raw.to_csv(meta['SWFilename'], index=False, header=True)
            logger.info('severe weather available : %s' % meta['SWFilename'])

        df = pd.merge(df, df_sw, how='left', on='ZTime')

    _dataframe_convert_local_time(df, local_time_zone)

    if dump_csv and df is not None:
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        meta['Filename'] = '%s%s-%s-%s.csv' % (result_dir, address,
                                               date_start.strftime('%Y%m%d'), date_end.strftime('%Y%m%d'))
        df.to_csv(meta['Filename'], index=False, header=True)
        logger.info('weather available : %s' % meta['Filename'])

    df.meta = meta

    return df


def get_weather_lite(date_start, date_end, station2location):
    date_end += datetime.timedelta(hours=23)
    year_start, year_end = date_start.year, date_end.year
    df, stations = None, {}
    for year in xrange(year_start, year_end+1):
        for usaf_wban, location in station2location.items():
            if not fetcher.fetch_raw_lite(year, usaf_wban):
                logger.error('cannot find %s-%d miles:%d' % (usaf_wban, year, location[0]))
                continue
            logger.info('parsed %s-%d %d miles at %s' % (usaf_wban, year, location[0], location[3]))
            m1, d1, m2, d2, h1, h2 = 1, 1, 12, 31, 0, 23
            if year == date_start.year:
                m1, d1, h1 = date_start.month, date_start.day, date_start.hour
            if year == date_end.year:
                m2, d2, h2 = date_end.month, date_end.day, date_end.hour
            df_temp = parser.parse_raw_lite(usaf_wban, year, m1, d1, h1, m2, d2, h2)
            df = df_temp if df is None else df.append(df_temp)
            stations[year] = location[3], usaf_wban.split('-')[0], usaf_wban.split('-')[1], location[0], location[1], location[2]
            break
        else:
            return 'Fail %4d' % year
    df.stations = stations
    return df


def get_weather_severe(severe_weather, date_start, date_end, gps):
    response = fetcher.fetch_raw_severe_weather(severe_weather, date_start, date_end)
    if response is not 'OK':
        return None, None
    df_sw_raw = parser.parse_raw_severe_weather(severe_weather, date_start, date_end, gps)
    cols = ['ZTime' if col == '#ZTIME' else col.title() for col in df_sw_raw.columns.values]
    df_sw_raw.columns = cols

    # integrate hourly
    hour2reports = collections.defaultdict(dict)
    for i in xrange(len(df_sw_raw)):
        t, event, source = df_sw_raw.iloc[i][['ZTime', 'Event', 'Source']]
        t = t/10000*10000
        if event in hour2reports[t]:
            hour2reports[t][event][source] += 1
        else:
            hour2reports[t][event] = collections.Counter({source: 1})

    times, events, sources = [], [], []
    for t in sorted(hour2reports.keys()):
        event = max(hour2reports[t].keys(), key=lambda e: sum(hour2reports[t][e][s] for s in hour2reports[t][e]))
        source = ', '.join(['%d %s' % (n, s) for s, n in hour2reports[t][event].iteritems()])
        times.append(t)
        events.append(event)
        sources.append(source)
    df_sw = pd.DataFrame(data={'ZTime': times, '%s.Event' % severe_weather.title(): events,
                               '%s.Source' % severe_weather.title(): sources})
    return df_sw, df_sw_raw


def summarize_daily(df_weather):
    reports, day_i = [], 0
    while day_i < len(df_weather):
        t = df_weather.iloc[day_i]['Time']
        if t == -9999 or t != t:
            day_i += 1
            continue
        day_j = min(day_i + 25, len(df_weather)-1)  # daylight saving
        while day_j > day_i and df_weather.iloc[day_j]['Time'] >= int(t)/1000000*1000000 + 240000:
            day_j -= 1
        day_s, summary = _summarize_day(df_weather, day_i, day_j)
        if day_s is not None and summary is not None:
            reports.append((day_s, summary))
        day_i = day_j + 1

    return reports


def _remove_nan(xx):
    return [x for x in xx if (x != -9999 and x == x)]


def _summarize_day(df_weather, day_i, day_j):
    df_daily = df_weather.iloc[day_i:day_j+1]
    ztimes, times, oat, wd, ws, sky, ppt, ppt6 = df_daily['ZTime'].values, \
        df_daily['Time'].values, df_daily['OAT'].values, df_daily['WD'].values, \
        df_daily['WS'].values, df_daily['SKY'].values, df_daily['PPT'].values, df_daily['PPT6'].values
    if len(_remove_nan(times)) < len(times)/2:
        logger.error('Too Few Records ' + ';'.join('%s:%s' % (k, v) for k, v in df_weather.info.items()))
        return None, None
    day_s = datetime.datetime.strptime(str(df_weather.iloc[day_j]['Time']), '%Y%m%d%H%M%S').strftime('%y/%m/%d %a')

    assert times[0]/1000000 == times[-1]/1000000    # assert same day

    oat = [int(round(t/10.0*1.8 + 32)) if (t == t and t != -9999) else -9999 for t in oat]
    sky = [s if s == s else -9999 for s in sky]
    sky = [s if s <= 10 else s-10 for s in sky]
    ws = [int(round(w/10.0*2.23694)) if (w == w and w != -9999) else -9999 for w in ws]
    ppt = [r/10.0 if (r == r and r != -9999) else -9999 for r in ppt]       # in mm
    ppt6 = [r/10.0 if (r == r and r != -9999) else -9999 for r in ppt6]     # in mm

    # todo rules to summarize daily report
    msg = 'Sunny'
    rain_sum = max(sum(_remove_nan(ppt)), sum(_remove_nan(ppt6)))
    if rain_sum >= 1.5:
        msg = 'Rainy'
        rain_hours = set()
        for h in xrange(1, day_j-day_i+1):
            if ppt6[h] >= 1:
                rain_hours |= set(range(h-6, h+1))
            if ppt[h] >= 1:
                rain_hours.add(h)
        if len(rain_hours) > 0:
            temperatures = [oat[h] for h in rain_hours]
            # if sum(temperatures)*1.0/len(temperatures) < 35:
            if min(temperatures) <= 32:
                msg = 'Snow'
    elif sum([1 for w in ws if w >= 20]) >= 5:
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

    # severe weather
    plsr = collections.OrderedDict()
    for h in xrange(day_j-day_i+1):
        e = df_daily.iloc[h]['Plsr.Event']
        if not e or e != e:
            continue
        if e in plsr:
            plsr[e].append(h)
        else:
            plsr[e] = [h]
    summary['Plsr'] = ', '.join(_translate(e) + ' at ' + ' '.join(['%d:00' % t for t in plsr[e]])
                                for e in plsr)
    return day_s, summary


def _get_time_zone(gps, dt):
    api_key = json.load(open('../../local/accounts.json'))['google_map_api_key']
    url = "https://maps.googleapis.com/maps/api/timezone/json?location=%f,%f&timestamp=%d&key=%s" \
          % (gps[0], gps[1], (dt - datetime.datetime(1970, 1, 1)).total_seconds(), api_key)
    response = json.loads(urllib2.urlopen(url).read())
    if response['status'] != 'OK':
        return response['status']
    return response['timeZoneId']


def _dataframe_convert_local_time(df, local_time_zone):
    local_time = [int(datetime.datetime.strptime(str(t), '%Y%m%d%H%M%S').replace(tzinfo=tz.gettz('UTC')).
                      astimezone(local_time_zone).strftime('%Y%m%d%H%M%S')) if t != -9999 else t
                  for t in df['ZTime'].values]
    df.insert(1, 'Time', pd.Series(local_time, index=df.index))


_mapping = {'SNOW': 'Snow', 'FLOOD': 'Flood', 'NON-TSTM WND DMG': 'Wind Damage',
            'DEBRIS FLOW': 'Debris Flow', 'COASTAL FLOOD': 'Coastal Flood',
            'HIGH SUST WINDS': 'High Winds', 'FLASH FLOOD': 'Flash Flood',
            'HEAVY RAIN': 'Heavy Rain', 'HAIL': 'Hail', 'LIGHTNING': 'Lightning',
            'NON-TSTM WND GST': 'High Winds', 'TSTM WND DMG': 'Wind Damage',
            'FREEZING RAIN': 'Freezing Rain', 'TSTM WND GST': 'Thunderstorm Winds'}


def _translate(event):
    # todo
    if event in _mapping:
        return _mapping[event]
    else:
        logger.error('Unknown event: ' + event)
        return event.title()
# if __name__ == '__main__':
