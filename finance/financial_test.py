from finance.filling import FillingParser
from finance.financial import FinancialFactory
import unittest
import os
from finance.financial import FinancialReport, Statement


class TestFinancialFactory(unittest.TestCase):
    def test_create(self):
        parser = FillingParser()
        fpath = os.path.join(os.path.dirname(__file__), 'xbrl_test.xml')
        filing = parser.parse(fpath)
        self.assertTrue(len(filing.facts) > 0)

        factory = FinancialFactory()
        financial = factory.create(filing)
        self.assertTrue(len(financial.statements) > 0)
        print(financial)

    def test_get_item(self):
        report = FinancialReport()
        stat = Statement("income")
        stat.add_item("item1", "USD", 1)
        report.add_stat(stat)
        self.assertEquals(report.get_stat_item_value("income", "item1"), 1)
