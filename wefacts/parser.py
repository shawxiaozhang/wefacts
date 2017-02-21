import pandas as pd


def _cal_day_gap(year, m1, d1, m2, d2):
    """
    left inclusive
    """
    month2days = {1: 31, 2: 28, 3: 31, 5: 31, 7: 31, 8: 31, 10: 31, 12: 31}
    if year % 4 == 0:
        month2days[2] = 29
    gap = d2 - d1
    for m in xrange(m1, m2):
        gap += month2days.get(m, 30)
    return gap


def parse_raw(sid, year, m1=1, d1=1, m2=12, d2=31):
    """
    :param sid:     station id
    :param year:
    :param m1:      start month, inclusive
    :param d1:      start day, inclusive
    :param m2:      end month, inclusive
    :param d2:      end day, inclusive
    :return rec:    records of temperature time series (an all-zero row if no record found)
    """
    filename = '../raw/%s-%4d.txt' % (sid, year)
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    row_num = 24 * (_cal_day_gap(year, m1, d1, m2, d2) + 1)
    columns = ['Date', 'Hour', 'OAT', 'DT', 'SLP', 'WD', 'WS', 'SKY', 'PPT', 'PPT6']
    df = pd.DataFrame(index=xrange(row_num), columns=columns)
    # df = df.fillna(-9999)
    i1 = 24 * _cal_day_gap(year, 1, 1, m1, d1)
    # row adjustment in case of missing records
    if i1 >= len(lines):
        i1 = len(lines) - 1
    while True:
        if i1 >= len(lines):
            break
        m, d, h = int(lines[i1][5:7]), int(lines[i1][8:11]), int(lines[i1][11:13])
        error = 24 * _cal_day_gap(year, m1, d1, m, d) + h
        if i1 < 0:
            i1 = 0
            break
        elif i1 == 0:
            error_prev = -1
        else:
            m, d, h = int(lines[i1-1][5:7]), int(lines[i1-1][8:11]), int(lines[i1-1][11:13])
            error_prev = 24 * _cal_day_gap(year, m1, d1, m, d) + h
        if error < 0:
            i1 += 1
        elif error == 0 or error_prev < 0:
            break
        else:
            i1 -= 1
    i2 = i1 + 24 * _cal_day_gap(year, m1, d1, m2, d2) + 24
    for line in lines[i1:i2]:
        nums = line[:4], line[5:7], line[8:11], line[11:13], line[13:19], line[19:25], \
               line[25:31], line[31:37], line[37:43], line[43:49], line[49:55], line[55:61]
        nums = [int(_) for _ in nums]
        row = 24 * _cal_day_gap(year, m1, d1, nums[1], nums[2]) + nums[3]
        if row >= row_num:
            break
        nums = [nums[0]*10000 + nums[1]*100 + nums[2]] + nums[3:]
        for field, num in zip(columns, nums):
            df.iloc[row][field] = num
        # rec[row][:] = nums[:]
    # df = pd.DataFrame(data=rec, columns=columns)
    return df


def test_sfo():
    # SFO Airport
    rec = parse_raw('724940-23234', 2017, 2, 6, 2, 6)
    # y, m, d, h, oat, dt, slp, wd, ws, sky, ppt, ppt6 = \
    row_num, _ = rec.shape
    for day in xrange(row_num/24):
        y, m, d = rec[day*24, 0:3]
        oats = rec[day*24:(day+1)*24, 4]*0.1
        winds = rec[day*24:(day+1)*24, 8]
        # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
        #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
    print rec


def test_sfo1():
    # redundant 20170101
    rec = parse_raw('724940-test1', 2017, 1, 2, 1, 2)
    row_num, _ = rec.shape
    for day in xrange(row_num/24):
        y, m, d = rec[day*24, 0:3]
        oats = rec[day*24:(day+1)*24, 4]*0.1
        winds = rec[day*24:(day+1)*24, 8]
        # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
        #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
    print rec


def test_sfo2():
    # missing 20170101
    rec = parse_raw('724940-test2', 2017, 1, 2, 1, 2)
    row_num, _ = rec.shape
    for day in xrange(row_num/24):
        y, m, d = rec[day*24, 0:3]
        oats = rec[day*24:(day+1)*24, 4]*0.1
        winds = rec[day*24:(day+1)*24, 8]
        # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
        #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
    print rec


def test_sfo3():
    # missing hours in 20170102
    rec = parse_raw('724940-test3', 2017, 1, 2, 1, 2)
    row_num, _ = rec.shape
    for day in xrange(row_num/24):
        y, m, d = rec[day*24, 0:3]
        oats = rec[day*24:(day+1)*24, 4]*0.1
        winds = rec[day*24:(day+1)*24, 8]
        # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
        #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
    print rec

if __name__ == '__main__':
    # test_sfo()
    test_sfo1()
    test_sfo2()
    test_sfo3()