import logging
import sys
import click
from basic.scraper import TickersScraper
from basic.ticker_repo_impl import TickerRepositoryImpl
from infrastructure.http.downloader import Downloader
from infrastructure import orm


@click.command()
@click.option('--batch', default=200, help='Number of batch size.')
@click.option('--apikey', default='', help='API Key for polygon')
@click.option('--retries', default=1, help='Retry times for a api request')
@click.option('--proxy', default='http://127.0.0.1:12639', help='Proxy for a api request')
@click.option('--dburl', default="mysql://root:123@localhost/stock", help='Database url')
def scrape(batch, apikey, retries, dburl, proxy):
    downloader = Downloader(retries, 0.1, {'http': proxy, 'https': proxy})
    session = orm.setup(dburl)
    repo = TickerRepositoryImpl(session)
    scraper = TickersScraper(downloader, repo, batch)
    scraper.scrape()


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    scrape()
