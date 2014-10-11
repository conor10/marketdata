import unittest

from feedhandlers import utils as utils


class TestUtils(unittest.TestCase):
    def test_trim_trailing_period(self):
        list = ['', 'ABC', 'DEF.']
        utils.trim_trailing_period(list)
        self.assertListEqual(['', 'ABC', 'DEF'], list)


if __name__ == '__main__':
    unittest.main()
