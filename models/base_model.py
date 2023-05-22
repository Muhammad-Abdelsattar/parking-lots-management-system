from sqlalchemy.ext.declarative import declarative_base
from core.database_config import engine


Base = declarative_base()

def init_models():
    Base.metadata.create_all(engine)
