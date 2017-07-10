"""
Parse raw weather records.
"""

import datetime

import pandas as pd
import numpy as np

import util


def _cal_day_gap(year, month_start, day_start, month_end, day_end):
    month2days = {1: 31, 2: 28, 3: 31, 5: 31, 7: 31, 8: 31, 10: 31, 12: 31}
    if year % 4 == 0:
        month2days[2] = 29
    gap = day_end - day_start
    for m in xrange(month_start, month_end):
        gap += month2days.get(m, 30)
    return gap


def parse_raw_lite(
        usaf_wban, year, dir_raw,
        month_start=1, day_start=1, hour_start=0,
        month_end=12, day_end=31, hour_end=23):
    """
    :param usaf_wban:       station id
    :param year:
    :param month_start:     start month, inclusive
    :param day_start:       start day, inclusive
    :param month_end:       end month, inclusive
    :param day_end:         end day, inclusive
    :return rec:            pandas data frame, weather records
    """
    filename = '%s%s-%4d.txt' % (dir_raw, usaf_wban, year)
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    row_num = 24 * _cal_day_gap(year, month_start, day_start, month_end, day_end) + hour_end - hour_start + 1
    columns = ['ZTime', 'OAT', 'DT', 'SLP', 'WD', 'WS', 'SKY', 'PPT', 'PPT6']

    data = np.empty((row_num, len(columns)), dtype=int)
    data.fill(-9999)

    i1 = 24 * _cal_day_gap(year, 1, 1, month_start, day_start) + hour_start
    # row adjustment in case of missing records
    if i1 >= len(lines):
        i1 = len(lines) - 1
    while True:
        if i1 >= len(lines):
            break
        m, d, h = int(lines[i1][5:7]), int(lines[i1][8:11]), int(lines[i1][11:13])
        error = 24 * _cal_day_gap(year, month_start, day_start, m, d) + h - hour_start
        if i1 < 0:
            i1 = 0
            break
        elif i1 == 0:
            error_prev = -1
        else:
            m, d, h = int(lines[i1-1][5:7]), int(lines[i1-1][8:11]), int(lines[i1-1][11:13])
            error_prev = 24 * _cal_day_gap(year, month_start, day_start, m, d) + h - hour_start
        if error < 0:
            i1 += 1
        elif error == 0 or error_prev < 0:
            break
        else:
            i1 -= 1
    i2 = i1 + 24 * _cal_day_gap(year, month_start, day_start, month_end, day_end) + 24 + hour_end - hour_start
    for line in lines[i1:i2]:
        nums = line[:4], line[5:7], line[8:11], line[11:13], line[13:19], line[19:25], \
            line[25:31], line[31:37], line[37:43], line[43:49], line[49:55], line[55:61]
        nums = [int(_) for _ in nums]
        row = 24 * _cal_day_gap(year, month_start, day_start, nums[1], nums[2]) + nums[3] - hour_start
        if row >= row_num:
            break
        nums = [(nums[0]*1000000 + nums[1]*10000 + nums[2]*100 + nums[3])*10000] + nums[4:]
        data[row][:] = nums
    return pd.DataFrame(data=data, columns=columns, dtype=np.int)


def parse_raw_severe_weather(category, date_start, date_end, gps, dir_raw, radius_degree=0.15,):
    df = None
    current_year, current_month = datetime.datetime.now().year, datetime.datetime.now().month
    for year in xrange(date_start.year, date_end.year+1):
        if year < current_year:
            df_temp = pd.read_csv('%s%s-%4d.csv' % (dir_raw, category, year), header=2, escapechar='\\')
            df_temp = _filter(df_temp, gps, date_start, date_end, radius_degree)
            df = df_temp if df is None else df.append(df_temp)
        elif year == current_year:
            m1 = 1 if date_start.year < current_year else date_start.month
            m2 = date_end.month
            for month in xrange(m1, m2+1):
                df_temp = pd.read_csv('%s%s-%4d%02d.csv' % (dir_raw, category, year, month), header=2, escapechar='\\')
                df_temp = _filter(df_temp, gps, date_start, date_end, radius_degree)
                df = df_temp if df is None else df.append(df_temp)
    df.sort_values('#ZTIME', inplace=True)
    return df


def _filter(df, gps, dt_start, dt_end, radius_degree):
    t1 = int(dt_start.strftime('%Y%m%d%H%M%S'))
    t2 = int((dt_end + datetime.timedelta(days=1)).strftime('%Y%m%d%H%M%S'))
    lat, lng = gps[0], gps[1]

    i_lat1 = lat - radius_degree <= df['LAT']
    i_lat2 = df['LAT'] <= lat + radius_degree
    i_lng1 = lng - radius_degree <= df['LON']
    i_lng2 = df['LON'] <= lng + radius_degree
    i_time1 = t1 <= df['#ZTIME']
    i_time2 = df['#ZTIME'] <= t2
    return df.loc[i_lat1 & i_lat2 & i_lng1 & i_lng2 & i_time1 & i_time2]


