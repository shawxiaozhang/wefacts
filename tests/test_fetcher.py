from unittest import TestCase
import datetime

from wefacts import fetcher


class TestFetcher(TestCase):
    def test_fetch_123456_12345(self):
        self.assertFalse(fetcher.fetch_raw_lite(2015, '123456-12345', retry=3))

    def test_fetch_724940_23234(self):
        self.assertFalse(fetcher.fetch_raw_lite(8899, '724940-23234', retry=3))
        self.assertIs(len(fetcher.fetch_raw_lite(2009, '724940-23234', retry=1)), 1)

    def test_fetch_plsr(self):
        self.assertIs(len(fetcher.fetch_raw_severe_weather('plsr', 2016)), 1)
        self.assertIs(len(fetcher.fetch_raw_severe_weather('plsr', 2014, 10)), 1)
        self.assertIs(len(fetcher.fetch_raw_severe_weather('plsr', datetime.datetime.now().year, 1)), 1)
        self.assertIs(len(fetcher.fetch_raw_severe_weather('plsr', datetime.datetime.now().year, retry=1)),
                      datetime.datetime.now().month)
