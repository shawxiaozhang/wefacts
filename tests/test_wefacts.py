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

    # todo parse/decode the full ish format raw data
