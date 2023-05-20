from sqlalchemy.ext.declarative import declarative_base
from core.database_config import engine,test_engine


Base = declarative_base()

def init_test_models():
    Base.metadata.create_all(test_engine)

def init_models():
    Base.metadata.create_all(engine)
