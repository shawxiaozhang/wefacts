from unittest import TestCase
from ftplib import FTP
import datetime

from wefacts import searcher


class TestSearcher(TestCase):
    def test_stations_quality_US(self):
        df_station = searcher.load_stations('US')
        good, poor = 0, 0
        for i in xrange(len(df_station)):
            usaf, wban = df_station.iloc[i][['USAF', 'WBAN']]
            if usaf == 999999 or wban == 99999:
                poor += 1
            else:
                good += 1
        self.assertGreater(good, poor)
        self.assertGreater(good, 1500)

    def test_stations_China(self):
        end_time = int((datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y%m%d'))
        df_station = searcher.load_stations(country='CH', state=None, date_weather_end=end_time)
        good, poor = 0, 0
        for i in xrange(len(df_station)):
            usaf, wban, lat, lng = df_station.iloc[i][['USAF', 'WBAN', 'LAT', 'LON']]
            if usaf == 999999 or wban == 99999:
                poor += 1
            else:
                good += 1
        self.assertGreaterEqual(good+poor, 200)

    def test_stations_Switzerland(self):
        end_time = int((datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y%m%d'))
        df_station = searcher.load_stations(country='SW', state=None, date_weather_end=end_time)
        good, poor = 0, 0
        for i in xrange(len(df_station)):
            usaf, wban, lat, lng = df_station.iloc[i][['USAF', 'WBAN', 'LAT', 'LON']]
            if usaf == 999999 or wban == 99999:
                poor += 1
            else:
                good += 1
        self.assertGreaterEqual(good+poor, 100)

    def test_check_lite_stations(self):
        stations_lite = set()
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()
        ftp.cwd('pub/data/noaa/isd-lite/%d' % 2017)
        for f in ftp.nlst():
            usaf, wban, suffix = str(f).split('-')
            stations_lite.add(usaf + '-' + wban)
        ftp.quit()

        in_lite, not_lite = set(), set()
        df_stations_all = searcher.load_stations(country='US')
        for i in xrange(len(df_stations_all)):
            usaf, wban = df_stations_all.iloc[i][['USAF', 'WBAN']]
            station = '%6d-%05d' % (usaf, wban)
            if station in stations_lite:
                in_lite.add(station)
            else:
                not_lite.add(station)
        self.assertLessEqual(len(not_lite), 10)
        self.assertLessEqual(len(not_lite)/len(in_lite), 0.01)

    # todo station quality diagnose: upload every 3 hours, no precipitation, no wind
