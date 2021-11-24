from stock.daily_price import DailyPriceRepository, DailyPrice
from typing import List
from influxdb import InfluxDBClient


class TickerRepositoryImpl(DailyPriceRepository):
    def __init__(self, client: InfluxDBClient) -> None:
        self.client = client

    def query(self, query):
        pass

    def batch_save(self, tickets: List[DailyPrice]):
        pass
