import unittest
from basic.ticker import Ticker
from basic.ticker_repo_impl import TickerRepositoryImpl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.base import Base


class TestTickerRepoImpl(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=True)
        self.session = sessionmaker(bind=engine)()
        Base.metadata.create_all(engine)
        self.session.commit()

    def test_save(self):
        repo = TickerRepositoryImpl(session=self.session)
        tk1 = Ticker(symbol="cik1", name="tickername")
        repo.save(tk1)
        found = repo.find_by_symbol("cik1")
        self.assertEquals(tk1.name, found.name)

        tk2 = Ticker(symbol="cik2", name="tickername")
        repo.batch_save([tk1, tk2])
        found = repo.find_range(1, 2)
