from finance.scraper import FilingIndex, FilingIndexGroup, FilingScraper
from finance.scraper import Downloader, DownloaderFactory
import unittest


class TestDownloader(unittest.TestCase):
    def test_get_content(self):
        downloader = Downloader(1, 0.1)
        page = downloader.get_content("https://cn.bing.com/")
        self.assertTrue(len(page) > 0)


class TestFilingScraper(unittest.TestCase):
    def test_load_urls(self):
        downloader_factory = DownloaderFactory()
        filing_scraper = FilingScraper(downloader_factory)
        filing_scraper.load_index_group("aapl")

    def test_download(self):
        downloader_factory = DownloaderFactory()
        filing_scraper = FilingScraper(downloader_factory)
        co_filings = FilingIndexGroup
        index = FilingIndex(
            "2020-01-01",
            ["https://www.sec.gov/Archives/edgar/data/320193/000032019319000066/a10-qq220193302019_htm.xml"])
        co_filings.indexes = [index]
        co_filings.symbol = "aapl"
        filing_scraper.download(index_group=co_filings,
                                save_path_base="F:\\pythonProjects\\tmp")


if __name__ == '__main__':
    unittest.main()
