from pathlib import Path
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter
from faker import Faker
import csv
import codecs


DEFAULT_RETRIES = 10
RATE_LIMIT_SLEEP_INTERVAL = 0.1


class Downloader(object):
    """Used to download from url and save to file"""
    fake = Faker()

    def __init__(self, retries, backoff_factor, proxies=None) -> None:
        retry = Retry(
            total=retries > 0 and retries or DEFAULT_RETRIES,
            backoff_factor=backoff_factor > 0 and backoff_factor or RATE_LIMIT_SLEEP_INTERVAL,
            status_forcelist=[403, 500, 502, 503, 504],
        )
        self.proxies = proxies
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

    def get_csvreader(self, url) -> str:
        print('get content from:{0}'.format(url))
        r = self.client.get(url, headers={"User-Agent": self._random_user_agent()},
                            proxies=self.proxies, stream=True)
        r.raise_for_status()
        return csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=',', quotechar='"')

    def get_content(self, url) -> str:
        print('get content from:{0}'.format(url))
        resp = self.client.get(url, headers={"User-Agent": self._random_user_agent()},
                               proxies=self.proxies)
        resp.raise_for_status()
        return resp.text

    def _random_user_agent(self) -> str:
        fake = Downloader.fake
        return f"{fake.first_name()} {fake.last_name()} {fake.email()}"


class DownloaderFactory(object):
    def create(self):
        return Downloader(10, 0.1)
