from dataclasses import dataclass
from finance.filling import Filling, FillingRepository, FillingFact
from sqlalchemy import Column, Integer, Float, String, ForeignKey, select
from sqlalchemy.orm import relationship, Session
from orm.base import Base
import json


@dataclass
class FillingDTO(Base):
    __tablename__ = 'filling'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    type = Column(String)
    report_date = Column(String)
    period_end_date = Column(String)
    adsh = Column(String)

    facts = relationship("FillingFactDTO")


@dataclass
class FillingFactDTO(Base):
    __tablename__ = 'filling_fact'
    filling_id = Column(Integer, ForeignKey('filling.id'))
    tag = Column(String, primary_key=True)
    end_date = Column(String, primary_key=True)
    members = Column(String, primary_key=True)
    uom = Column(String)
    value = Column(Float)
    qtrs = Column(Integer)


class FillingRepositoryImpl(FillingRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def findall_by_symbol(self, symbol):
        pass

    def _filling_dto_to_model(self, dto: FillingDTO):
        filling = Filling(id=dto.id, symbol=dto.symbol, type=dto.type, adsh=dto.adsh,
                          report_date=dto.report_date, period_end_date=dto.period_end_date)
        facts = []
        for fact_dto in dto.facts:
            fact = self._fact_dto_to_model(fact_dto)
            facts.append(fact)
        filling.facts = facts
        return filling

    def _fact_dto_to_model(self, dto: FillingFactDTO):
        return FillingFact(dto.tag, json.loads(dto.members), dto.end_date,
                           dto.qtrs, dto.uom, dto.value)

    def _fact_model_to_dto(self, fact: FillingFact):
        return FillingFactDTO(tag=fact.key.tag, end_date=fact.key.end_date,
                              members=json.dumps(fact.key.members),
                              uom=fact.uom, value=fact.value, qtrs=fact.qtrs)

    def _filling_model_to_dto(self, filing: Filling):
        dto = FillingDTO(adsh=filing.adsh, type=filing.type, id=filing.id, symbol=filing.symbol,
                         report_date=filing.report_date, period_end_date=filing.period_end_date)
        fact_dtos = []
        for fact in filing.facts.values():
            fact_dto = self._fact_model_to_dto(fact)
            fact_dto.filling_id = dto.id
            fact_dtos.append(fact_dto)
        dto.facts = fact_dtos
        return dto

    def find_by_symbol_period(self, symbol, period) -> Filling:
        stmt = select(FillingDTO).where(FillingDTO.symbol == symbol).where(
            FillingDTO.period_end_date == period)
        dto = self.session.execute(stmt).scalar_one()
        print(dto)
        return self._filling_dto_to_model(dto)

    def save(self, filling: Filling):
        dto = self._filling_model_to_dto(filling)
        self.session.add(dto)
        self.session.flush()
