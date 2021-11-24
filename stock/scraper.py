from infrastructure.http.downloader import Downloader
from stock.daily_price import DailyPrice, DailyPriceRepository

URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'\
    '&symbol={}&apikey={}&datatype=json&outputsize={}&datatype=csv'
OUPUTSIZE_FULL = "full"
OUPUTSIZE_LATEST = "compact"
DEFAULT_BATCH_SAVE_SIZE = 100
DEFAULT_API_KEY = "ZJ1RDHHULZH8OHCH"


class DailyPriceScraper(object):

    def __init__(self,  downloader: Downloader, repository: DailyPriceRepository,
                 batch_save_size=DEFAULT_BATCH_SAVE_SIZE, apikey=DEFAULT_API_KEY) -> None:
        self.downloader = downloader
        self.repository = repository
        if not apikey:
            apikey = DEFAULT_API_KEY
        self.apikey = apikey
        if batch_save_size <= 0 or batch_save_size > 400:
            batch_save_size = DEFAULT_BATCH_SAVE_SIZE
        self.batch_save_size = batch_save_size

    def scrape(self, symbol, load_full=False):
        link = URL.format(symbol, self.apikey,
                          OUPUTSIZE_FULL if load_full else OUPUTSIZE_LATEST)
        reader = self.downloader.get_csvreader(link)
        tickers = []
        count = -1
        for row in reader:
            count = count+1
            if count == 0:
                continue
            tickers.append(DailyPrice(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

            if count % self.batch_save_size != 0:
                continue
            self.repository.batch_save(tickers)
            tickers = []
        if len(tickers) > 0:
            self.repository.batch_save(tickers)
