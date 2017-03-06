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
        self.assertGreater(len(records), 1)

    def test_Seattle_rainy_days(self):
        df = wefacts.get_weather('Seattle', 20160101, 20161231)
        records = wefacts.summarize_daily(df)
        count_rainy = 0
        for d, summary in records:
            if summary['MSG'] == 'Rainy':
                count_rainy += 1
        self.assertGreater(count_rainy, 30)

    # todo test rainy sunny snow days over the year for San Franciso, Seattle, Chicago, Boston

    # todo parse/decode the full ish format raw data
