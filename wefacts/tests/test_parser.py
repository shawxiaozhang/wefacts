from unittest import TestCase

import wefacts


class TestParser(TestCase):
    def test_is_string(self):
        # s = wefacts.
        s = '321'
        self.assertTrue(isinstance(s, basestring))