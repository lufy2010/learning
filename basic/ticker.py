from dataclasses import dataclass
from typing import List


@dataclass
class Ticker:
    symbol: str = ""
    name: str = ""
    exchange: str = ""
    exchange_short_name: str = ""
    type: str = ""


class TickerRepository:
    def find_range(self, offset, limit):
        pass

    def batch_save(self, tickets: List[Ticker]):
        pass

    def save(self, ticker: Ticker):
        pass
