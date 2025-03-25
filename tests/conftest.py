import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

@pytest.fixture
def test_db_url():
    return "sqlite:///:memory:"

@pytest.fixture
def test_engine(test_db_url):
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture
def test_session_maker(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)