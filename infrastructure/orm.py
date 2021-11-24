import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.base import Base


@contextlib.contextmanager
def transaction(session):
    if not session.in_transaction():
        with session.begin():
            yield
    else:
        yield


def setup(url):
    engine = create_engine(url, echo=True)
    session = sessionmaker(bind=engine)()
    Base.metadata.create_all(engine)
    session.commit()
    return session
