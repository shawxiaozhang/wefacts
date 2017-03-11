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
        # df = wefacts.get_weather('Squirrel Hill', 20161224, 20170106, False)
        df = wefacts.get_weather('Daly City', 20170303, 20170308, True)
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
                self.assertGreater(t, -10)
                self.assertLess(t, 40)
        self.assertEqual(len(temperature), (366 + 14) * 24)
        self.assertLessEqual(count_nan, 10)

    def test_yesterday_weather(self):
        import urllib2
        import json
        import datetime
        # geo-locate the connecting IP
        f = urllib2.urlopen('http://freegeoip.net/json/')
        json_string = f.read()
        f.close()
        location = json.loads(json_string)
        lat, lng = location['latitude'], location['longitude']
        date1 = int((datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d'))
        df = wefacts.get_weather('%f, %f' % (lat, lng), date1, date1)
        records = wefacts.summarize_daily(df)
        self.assertGreaterEqual(len(records), 1)

    def test_Pittsburgh(self):
        df = wefacts.get_weather('Daly City', 20170307, 20170309, dump_csv=True)
        print len(df)
        for i in xrange(len(df)):
            print df.iloc[i]['ZTime'], df.iloc[i]['Time'], df.iloc[i]['OAT']/10.0, df.iloc[i]['WS']/10.0

    def test_Seattle_rainy_days(self):
        df = wefacts.get_weather('SEATTLE', 20160101, 20161231)
        records = wefacts.summarize_daily(df)
        count_rainy = 0
        for d, summary in records:
            if summary['MSG'] == 'Rainy':
                count_rainy += 1
        self.assertGreater(count_rainy, 35)

    def test_Boston_snow_days(self):
        # todo
        df = wefacts.get_weather('Boston', 20160101, 20161231)
        records = wefacts.summarize_daily(df)
        count_snow = 0
        for d, summary in records:
            if summary['MSG'] == 'Snow':
                count_snow += 1
        self.assertGreater(count_snow, 11)

    def test_LA_sunny_days(self):
        df = wefacts.get_weather('Beverly Hills', 20160101, 20161231)
        records = wefacts.summarize_daily(df)
        count_sunny = 0
        for d, summary in records:
            if summary['MSG'] == 'Sunny':
                count_sunny += 1
        self.assertGreater(count_sunny, 300)

    def test_SFO_windy_days(self):
        df = wefacts.get_weather('SAN FRANCISCO INTERNATIONAL AIRPORT', 20160101, 20161231)
        records = wefacts.summarize_daily(df)
        count_windy = 0
        for d, summary in records:
            if summary['MSG'] == 'Windy':
                count_windy += 1
        self.assertGreater(count_windy, 80)

