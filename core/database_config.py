from sqlalchemy import create_engine
from databases import Database
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from .config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URI = settings.DATABASE_URI

test_database_uri = "sqlite:///test_parking_database.db"

database = Database(SQLALCHEMY_DATABASE_URI)

database_test = Database(SQLALCHEMY_DATABASE_URI)

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    # connect_args={"check_same_thread": False},
)

test_engine = create_engine(
    test_database_uri,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

tset_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database():
    return database

def get_test_database():
    return database_test
