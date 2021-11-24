from infrastructure.http.downloader import Downloader
from basic.ticker import Ticker, TickerRepository
import json


TICKERS_NAV_URL = 'https://financialmodelingprep.com/api/v3/stock/list?apikey={}'
DEFAULT_BATCH_SAVE_SIZE = 100
DEFAULT_API_KEY = "3ad02b0884741c3e5db6a6759dfdbf75"


class TickersScraper(object):

    def __init__(self,  downloader: Downloader, tiker_repo: TickerRepository,
                 batch_save_size=DEFAULT_BATCH_SAVE_SIZE, apikey=DEFAULT_API_KEY) -> None:
        self.downloader = downloader
        self.tiker_repo = tiker_repo
        if not apikey:
            apikey = DEFAULT_API_KEY
        self.apikey = apikey
        if batch_save_size <= 0 or batch_save_size > 400:
            batch_save_size = DEFAULT_BATCH_SAVE_SIZE
        self.batch_save_size = batch_save_size

    def scrape(self):
        link = TICKERS_NAV_URL.format(self.apikey)
        text = self.downloader.get_content(link)
        data = json.loads(text)
        if isinstance(data, dict):
            raise RuntimeError(data.get("Error Message"))
        tickers = []
        count = 0
        for r in data:
            tickers.append(Ticker(r.get('symbol'), r.get('name'), r.get('exchange'),
                                  r.get('exchangeShortName'), r.get('type')))
            count = count+1
            if count % self.batch_save_size != 0:
                continue
            self.tiker_repo.batch_save(tickers)
            tickers = []
        if len(tickers) > 0:
            self.tiker_repo.batch_save(tickers)
