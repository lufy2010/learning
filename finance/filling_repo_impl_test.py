import unittest
from finance.filling import Filling, FillingFact

from finance.filling_repo_impl import FillingRepositoryImpl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.base import Base


class TestFillingRepoImpl(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=True)
        self.session = sessionmaker(bind=engine)()
        Base.metadata.create_all(engine)
        self.session.commit()

    def test_save(self):
        repo = FillingRepositoryImpl(session=self.session)
        filling = Filling(symbol="appl", type="10-Q", period_end_date="2021-01-01")
        fact = FillingFact("tag", {"mem": "memval"}, "2021-01-01", 1, "USD", 2.0)
        filling.add_fact(fact)
        repo.save(filling)

        filling_loaded = repo.find_by_symbol_period("appl", "2021-01-01")
        self.assertIsNotNone(filling_loaded)
        self.assertEquals(filling_loaded.symbol, filling.symbol)
