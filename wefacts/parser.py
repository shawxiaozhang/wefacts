"""
Parse raw weather records.
"""

import pandas as pd


def _cal_day_gap(year, month_start, day_start, month_end, day_end):
    month2days = {1: 31, 2: 28, 3: 31, 5: 31, 7: 31, 8: 31, 10: 31, 12: 31}
    if year % 4 == 0:
        month2days[2] = 29
    gap = day_end - day_start
    for m in xrange(month_start, month_end):
        gap += month2days.get(m, 30)
    return gap


def parse_raw_lite(usaf_wban, year, month_start=1, day_start=1, month_end=12, day_end=31):
    """
    :param usaf_wban:       station id
    :param year:
    :param month_start:     start month, inclusive
    :param day_start:       start day, inclusive
    :param month_end:       end month, inclusive
    :param day_end:         end day, inclusive
    :return rec:            pandas data frame, weather records
    """
    filename = '../raw/%s-%4d.txt' % (usaf_wban, year)
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    row_num = 24 * (_cal_day_gap(year, month_start, day_start, month_end, day_end) + 1)
    columns = ['Date', 'Hour', 'OAT', 'DT', 'SLP', 'WD', 'WS', 'SKY', 'PPT', 'PPT6']
    df = pd.DataFrame(index=xrange(row_num), columns=columns)
    i1 = 24 * _cal_day_gap(year, 1, 1, month_start, day_start)
    # row adjustment in case of missing records
    if i1 >= len(lines):
        i1 = len(lines) - 1
    while True:
        if i1 >= len(lines):
            break
        m, d, h = int(lines[i1][5:7]), int(lines[i1][8:11]), int(lines[i1][11:13])
        error = 24 * _cal_day_gap(year, month_start, day_start, m, d) + h
        if i1 < 0:
            i1 = 0
            break
        elif i1 == 0:
            error_prev = -1
        else:
            m, d, h = int(lines[i1-1][5:7]), int(lines[i1-1][8:11]), int(lines[i1-1][11:13])
            error_prev = 24 * _cal_day_gap(year, month_start, day_start, m, d) + h
        if error < 0:
            i1 += 1
        elif error == 0 or error_prev < 0:
            break
        else:
            i1 -= 1
    i2 = i1 + 24 * _cal_day_gap(year, month_start, day_start, month_end, day_end) + 24
    for line in lines[i1:i2]:
        nums = line[:4], line[5:7], line[8:11], line[11:13], line[13:19], line[19:25], \
               line[25:31], line[31:37], line[37:43], line[43:49], line[49:55], line[55:61]
        nums = [int(_) for _ in nums]
        row = 24 * _cal_day_gap(year, month_start, day_start, nums[1], nums[2]) + nums[3]
        if row >= row_num:
            break
        nums = [nums[0]*10000 + nums[1]*100 + nums[2]] + nums[3:]
        for field, num in zip(columns, nums):
            df.iloc[row][field] = num
    return df
