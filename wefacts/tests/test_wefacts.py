from unittest import TestCase

from wefacts import wefacts


class TestWeFacts(TestCase):
    def test_Boston_1997_AprilFoolStorm(self):
        df = wefacts.get_weather('Boston', 19970331, 19970401, False)
        precipitation = df['PPT'].values
        print precipitation
        print sum(precipitation)
        self.assertGreater(sum(precipitation), 300)

    def test_Pittsburgh_1950_BigSnow(self):
        df = wefacts.get_weather('Pittsburgh', 19501124, 19501130, False)
        precipitation = df['PPT'].values
        print precipitation
        print sum(precipitation)
        self.assertGreater(sum(precipitation), 300)




# from ftplib import FTP
# import os
#
# import pandas as pd
# import matplotlib.pyplot as plt
#
# import stations
# import parser
# from util import *
#
# def _plot_weather(values, time_start, time_end, label=''):
#     # todo interpolation
#     i = 0
#     while values[i] == -9999:
#         i += 1
#         if i >= len(values):
#             logger.error('error in weather data : all -9999')
#             return
#     for j in xrange(i):
#         values[j] = values[i]
#     while i < len(values):
#         if values[i] == -9999:
#             values[i] = values[i - 1]
#         i += 1
#
#     y_unit = ''
#     if label == 'OAT':
#         values = [x / 10.0 for x in values]
#         y_unit = 'Celsius'
#     elif label == 'WS':
#         values = [x * 0.223694 for x in values]
#         y_unit = 'mph'
#     elif label == 'PPT':
#         y_unit = 'mm'
#
#     plt.figure()
#     plt.plot(xrange(len(values)), values, label=label)
#     plt.xticks(xrange(0, len(values), 24))
#     plt.xlabel('%d - %d' % (time_start, time_end))
#     plt.ylabel(y_unit)
#     plt.grid()
#     plt.show()
#
#
# def test_get_weather_cross_year():
#     address, time_start, time_end, result_dir = 'squirrel hill', 20161224, 20170107, '../result/'
#     get_weather(address, time_start, time_end, True, result_dir)
#     df = pd.read_csv('%s%s-%d-%d.csv' % (result_dir, address, time_start, time_end))
#     for label in ['OAT', 'WS', 'PPT']:
#         values = df[label].values
#         _plot_weather(values, time_start, time_end, label=label)
#
#
# def test_cmp_stations():
#     ftp_ids = set()
#     ftp = FTP('ftp.ncdc.noaa.gov')
#     ftp.login()
#     ftp.cwd('pub/data/noaa/isd-lite/%d' % 2017)
#     # ftp.cwd('pub/data/noaa/%d' % 2017)
#     for f in ftp.nlst():
#         usaf, wban, suffix = str(f).split('-')
#         ftp_ids.add(usaf + '-' + wban)
#     ftp.quit()
#
#     found, miss = set(), set()
#     df_isd = stations.load_stations(country='US')
#     for i in xrange(len(df_isd)):
#         usaf, wban = df_isd.iloc[i][['USAF', 'WBAN']]
#         name = '%6d-%05d' % (usaf, wban)
#         if name in ftp_ids:
#             found.add(name)
#         else:
#             miss.add(name)
#     print len(ftp_ids), len(df_isd)
#     print len(found), len(miss), 1.0*len(miss)/(len(found)+len(miss))
#     print 'found', found
#     print 'miss', miss
#
#
# if __name__ == '__main__':
#     # test_cmp_stations()
#     # test_get_weather_cross_year()
#     # get_weather_csv('220 macdonald ave', 20170209, 20170216)
#     get_weather('220 macdonald ave', 20170219, 20170222)
#
#     # todo station quality analysis => every 3 hours? no rain?
#     # todo how to choose the best station? (precision, no rain data, no wind data)
#     # log output stating all possible stations, then let the users decide which one to use.
#
#     # todo decode parse the ish format (full weather record)
