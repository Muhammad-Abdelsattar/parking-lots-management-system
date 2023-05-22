from sqlalchemy import create_engine
from databases import Database
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from .config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URI = settings.DATABASE_URI

database = Database(SQLALCHEMY_DATABASE_URI)


engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    # connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database():
    return database
