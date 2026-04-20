import pytest
from server import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_client(db_session, monkeypatch):
    app = create_app(database_url=SQLALCHEMY_DATABASE_URL)
    with app.test_client() as c:
        yield c
