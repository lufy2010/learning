from lxml import etree
import os
from pathlib import Path
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter
from faker import Faker
from bs4 import BeautifulSoup

SEC_HOST = 'https://www.sec.gov'

CHECK_VALID_INDEX_PAGE_STR = './/table[@summary="Results"]'

FILING_INDEX_URL_HREF = './/a[@id="documentsbutton"]/@href'

FILINGDATA_URLS_XPATH = './/table[@class="tableFile" and @summary="Data Files"]'\
    '/tbody/tr/td/a/@href'

FILING_DATE_XPATH = './/div[@class="formGrouping"]/div[contains(text(),"Filing Date")]'\
    '/following-sibling::div[1]/text()'

FILINGDATA_IGNORE_SUFFIX = tuple(["_cal.xml", "_def.xml", "_lab.xml", "_pre.xml", ".xsd"])

SYMBOL_FILINGS_NAV_URL = 'https://www.sec.gov/cgi-bin/browse-edgar?'\
    'action=getcompany&CIK={0}&type={1}&dateb=&owner=exclude&count=1'

DEFAULT_RETRIES = 10
RATE_LIMIT_SLEEP_INTERVAL = 0.1


class FilingIndex(object):
    """A FilingIndex contains data file links of a filing."""

    def __init__(self, date, links) -> None:
        self.date: str = date
        self.file_links: list[str] = links


class FilingIndexGroup(object):
    """A FilingIndexGroup contains filing indexes for a company"""

    def __init__(self) -> None:
        self.symbol: str = ""
        self.index_urls: list[str] = []
        self.indexes: list[FilingIndex] = []


class Downloader(object):
    """Used to download from url and save to file"""
    fake = Faker()

    def __init__(self, retries, backoff_factor) -> None:
        retry = Retry(
            total=retries > 0 and retries or DEFAULT_RETRIES,
            backoff_factor=backoff_factor > 0 and backoff_factor or RATE_LIMIT_SLEEP_INTERVAL,
            status_forcelist=[403, 500, 502, 503, 504],
        )
        self.client = requests.Session()
        self.client.mount("http://", HTTPAdapter(max_retries=retry))
        self.client.mount("https://", HTTPAdapter(max_retries=retry))
        return

    def __del__(self):
        if self.client:
            self.client.close()

    def download(self, url, save_path):
        print('download from:{}, save to:{}'.format(url, save_path))
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self.get_content(url)
        path.write_text(content)
        return True

    def get_content(self, url) -> str:
        print('get content from:{0}'.format(url))
        resp = self.client.get(url, headers={"User-Agent": self._random_user_agent()})
        resp.raise_for_status()
        return resp.text

    def _random_user_agent(self) -> str:
        fake = Downloader.fake
        return f"{fake.first_name()} {fake.last_name()} {fake.email()}"


class DownloaderFactory(object):
    def create(self):
        return Downloader(10, 0.1)


class FilingScraper(object):
    """FilingScraper using a downloader to download and save filing files.
       The files will be saved to save_path_base/symbol/date/
    """

    def __init__(self,  downloader) -> None:
        self.downloader = downloader

    def scrape(self, symbol, save_path_base):
        index_group = self.load_index_group(symbol)
        self.download(index_group, save_path_base)

    def download(self, index_group: FilingIndexGroup, save_path_base):
        if not index_group.indexes:
            return
        for index in index_group.indexes:
            for link in index.file_links:
                save_path = os.path.join(save_path_base, index_group.symbol,
                                         index.date, os.path.split(link)[1])
                page = self.downloader.download(link, save_path)
                if not page:
                    continue
                print("downloaded datafile:{}".format(link))

    def load_index_group(self, symbol) -> FilingIndexGroup:
        index_group = FilingIndexGroup()
        index_group.symbol = symbol
        self._load_index_urls("10-K", index_group)
        self._load_index_urls("10-Q", index_group)
        self._load_indexes(index_group)
        return index_group

    def _get_indexes_page(self, symbol, type):
        link = SYMBOL_FILINGS_NAV_URL.format(symbol, type)
        page = self.downloader.get_content(link)
        selector = etree.HTML(page)
        if selector.xpath(CHECK_VALID_INDEX_PAGE_STR):
            return page
        else:
            print("get filings page fail,invalid content.url:{0}".format(link))
            return False

    def _load_index_urls(self, type, index_group: FilingIndexGroup):
        page = self._get_indexes_page(index_group.symbol, type)
        if not page:
            return
        selector = etree.HTML(page)

        for link in selector.xpath(FILING_INDEX_URL_HREF):
            link = SEC_HOST + link
            print("append index url:{}".format(link))
            index_group.index_urls.append(link)

    def _load_indexes(self, index_group: FilingIndexGroup):
        for index_url in index_group.index_urls:
            index = self._get_index(index_url)
            if not index:
                continue
            index_group.indexes.append(index)
        return

    def _get_index(self, index_url):
        page = self.downloader.get_content(index_url)
        soup = BeautifulSoup(page, 'html5lib')
        selector = etree.HTML(soup.prettify())
        file_links = []
        try:
            date = (selector.xpath(FILING_DATE_XPATH)[0]).strip()
            urls = selector.xpath(FILINGDATA_URLS_XPATH)
            for url in urls:
                if not (os.path.split(url)[1]).endswith(FILINGDATA_IGNORE_SUFFIX):
                    link = SEC_HOST + url.strip()
                    print("append datafile. date:{},link:{}".format(date, link))
                    file_links.append(link)
            return FilingIndex(date=date, links=file_links)
        except IndexError:
            return False
