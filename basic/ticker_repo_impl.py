from dataclasses import dataclass
from basic.ticker import TickerRepository, Ticker
from sqlalchemy import Column, String, select
from sqlalchemy.orm import Session
from orm.base import Base
from typing import List
from infrastructure import orm


@dataclass
class TickerDTO(Base):
    __tablename__ = 'ticker'
    symbol = Column(String(50), primary_key=True)
    name = Column(String(200))
    exchange = Column(String(50))
    exchange_short_name = Column(String(200))
    type = Column(String(50))


class TickerRepositoryImpl(TickerRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_symbol(self, symbol):
        stmt = select(TickerDTO).where(TickerDTO.symbol == symbol)
        dto = self.session.execute(stmt).scalar_one()
        return self._dto_to_model(dto)

    def find_range(self, offset, limit):
        stmt = select(TickerDTO).order_by(TickerDTO.symbol).slice(offset, offset+limit)
        dtos = self.session.execute(stmt).scalars()
        return [self._dto_to_model(dto) for dto in dtos]

    def _dto_to_model(self, tk: TickerDTO):
        return Ticker(symbol=tk.symbol, name=tk.name, exchange=tk.exchange,
                      exchange_short_name=tk.exchange_short_name, type=tk.type)

    def _model_to_dto(self, tk: Ticker):
        return TickerDTO(symbol=tk.symbol, name=tk.name, exchange=tk.exchange,
                         exchange_short_name=tk.exchange_short_name, type=tk.type)

    def batch_save(self, tickets: List[Ticker]):
        dtos = {tk.symbol: self._model_to_dto(tk) for tk in tickets}
        with orm.transaction(self.session):
            for each in self.session.query(TickerDTO).filter(TickerDTO.symbol.in_(dtos.keys())).all():
                self.session.merge(dtos.pop(each.symbol))
            self.session.add_all(dtos.values())
            self.session.flush()

    def save(self, ticker: Ticker):
        with orm.transaction(self.session):
            self.session.merge(self._model_to_dto(ticker))
            self.session.flush()
