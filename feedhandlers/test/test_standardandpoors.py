import io
import unittest

import feedhandlers.standardandpoors as sp

class TestStandardAndPoors(unittest.TestCase):
    def test_parse_response_sp500(self):
        with open('data/standardandpoors/SP500ConstituentsExport.xls', 'r') \
                as f:
            symbols = sp.parse_response(f)
        self.assertEqual(501, len(symbols))

    def test_parse_response_asx200(self):
        with open('data/standardandpoors/ASX200ConstituentsExport.xls', 'r') \
                as f:
            symbols = sp.parse_response(f)
        self.assertEqual(200, len(symbols))

    def test_parse_empty_response(self):
        self.assertRaises(TypeError, sp.parse_response, io.StringIO())

    def test_parse_changed_format(self):
        with open('data/standardandpoors/SP500ChangedConstituentsExport.xls',
                  'r') as f:
            self.assertRaises(sp.ProcessingException, sp.parse_response, f)

if __name__ == '__main__':
    unittest.main()
