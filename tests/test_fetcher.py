from unittest import TestCase

from wefacts import fetcher


class TestFetcher(TestCase):
    def test_fetch_123456_12345(self):
        self.assertFalse(fetcher.fetch_raw_lite(2015, '123456-12345', retry=3))

    def test_fetch_724940_23234(self):
        self.assertFalse(fetcher.fetch_raw_lite(2099, '724940-23234', retry=3))
        self.assertTrue(fetcher.fetch_raw_lite(2009, '724940-23234', retry=1, delete=True))
