from dataclasses import dataclass
from typing import List


@dataclass
class DailyPrice:
    date: str = ""
    open: float = 0
    high: float = 0
    low: float = 0
    close: float = 0
    adjusted_close: float = 0
    volume: float = 0
    dividend_amount: float = 0
    split_coefficient: float = 0


class DailyPriceRepository:
    def query(self, query):
        pass

    def batch_save(self, tickets: List[DailyPrice]):
        pass
