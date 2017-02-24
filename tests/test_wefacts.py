from unittest import TestCase

from wefacts import wefacts


class TestWeFacts(TestCase):
    def test_Boston_1997_AprilFoolStorm(self):
        df = wefacts.get_weather('Boston', 19970331, 19970401, False)
        precipitation = df['PPT'].values
        self.assertGreater(sum(precipitation), 300)

    def test_Pittsburgh_1950_BigSnow(self):
        df = wefacts.get_weather('Pittsburgh', 19501124, 19501130, False)
        precipitation = df['PPT'].values
        self.assertGreater(sum(precipitation), 300)

    def test_CrossYear_SquirrelHill(self):
        # todo nan in first hour of the year : interpolation
        df = wefacts.get_weather('Squirrel Hill', 20161224, 20170106, False)
        temperature = [t/10.0 for t in df['OAT'].values]
        self.assertEqual(len(temperature), 14*24)
        count_nan = 0
        for t in temperature:
            if t != t:
                count_nan += 1
            else:
                self.assertGreater(t, -30)
                self.assertLess(t, 40)
        self.assertLessEqual(count_nan, 1)

    def test_CrossYear_SFO(self):
        df = wefacts.get_weather('SFO', 20151224, 20170106, False)
        temperature = [t / 10.0 for t in df['OAT'].values]
        count_nan = 0
        for t in temperature:
            if t != t:
                count_nan += 1
            else:
                self.assertGreater(t, -30)
                self.assertLess(t, 40)
        self.assertEqual(len(temperature), (366 + 14) * 24)
        self.assertLessEqual(count_nan, 10)

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
