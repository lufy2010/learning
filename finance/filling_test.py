from finance.filling import FillingParser
import unittest
import os


class TestFillingParser(unittest.TestCase):
    def test_parse(self):
        parser = FillingParser()
        fpath = os.path.join(os.path.dirname(__file__), 'xbrl_test.xml')
        filling = parser.parse(fpath)
        self.assertTrue(len(filling.facts) > 0)
