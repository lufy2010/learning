
from typing import List
import unittest

from stock.scraper import DailyPriceScraper
from stock.daily_price import DailyPrice, DailyPriceRepository
from infrastructure.http.downloader import Downloader


class MockRepo(DailyPriceRepository):
    def query(self, query):
        pass

    def batch_save(self, tickets: List[DailyPrice]):
        pass


class TestScraper(unittest.TestCase):
    def test_scrape(self):
        downloader = Downloader(1, 0.1)
        repo = MockRepo()
        scraper = DailyPriceScraper(downloader, repo)
        scraper.scrape("IBM")
