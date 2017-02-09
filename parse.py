import numpy as np


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


def parse(sid, year, m1=1, d1=1, m2=12, d2=31):
    """
    :param sid:     station id
    :param year:
    :param m1:      start month, inclusive
    :param d1:      start day, inclusive
    :param m2:      end month, inclusive
    :param d2:      end day, inclusive
    :return rec:    records of temperature time series
    """

    filename = 'raw/%s-%4d' % (sid, year)
    f = open(filename, 'r')
    row_num = 24 * (_cal_day_gap(year, m1, d1, m2, d2) + 1)
    rec = np.empty(shape=(row_num, 12), dtype=int)
    rec[:] = np.nan

    # todo in case skipped rows

    i1 = 24 * _cal_day_gap(year, 1, 1, m1, d1)
    i2 = 24 * _cal_day_gap(year, 1, 1, m2, d2) + 24
    for line in f.readlines()[i1:i2]:
        # y, m, d, h, oat, dt, slp, wd, ws, sky, ppt, ppt6 = \
        nums = line[:4], line[5:7], line[8:11], line[11:13], line[13:19], line[19:24], \
               line[25:31], line[31:37], line[37:43], line[43:49], line[49:55], line[55:61]
        nums = [int(_) for _ in nums]
        row = 24 * _cal_day_gap(year, m1, d1, nums[1], nums[2]) + nums[3]
        if row >= row_num:  #
            break
        rec[row][:] = nums[:]
    f.close()

    return rec


def test_sfo():
    # SFO Airport
    rec = parse('724940-23234', 2017, 2, 6, 2, 7)
    # y, m, d, h, oat, dt, slp, wd, ws, sky, ppt, ppt6 = \
    row_num, _ = rec.shape
    for day in xrange(row_num/24):
        y, m, d = rec[day*24, 0:3]
        oats = rec[day*24:(day+1)*24, 4]*0.1
        winds = rec[day*24:(day+1)*24, 8]
        print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
              % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))

if __name__ == '__main__':
    np.set_printoptions(threshold='nan')
    test_sfo()