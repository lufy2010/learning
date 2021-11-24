
from typing import List
import unittest

from basic.scraper import TickersScraper
from basic.ticker import Ticker, TickerRepository
from infrastructure.http.downloader import Downloader


class MockTickerRepo(TickerRepository):
    def find_all(self):
        pass

    def save_all(self, tickets: List[Ticker]):
        print("tickers:", len(tickets))
        pass

    def save(self, ticker: Ticker):
        pass


class TestScraper(unittest.TestCase):
    def test_scrape(self):
        downloader = Downloader(1, 0.1)
        repo = MockTickerRepo()
        scraper = TickersScraper(downloader, repo)
        scraper.scrape()
