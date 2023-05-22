from sqlalchemy import NCHAR,DateTime, Boolean, Column, Integer,String, Float, ForeignKey, Enum
from .base_model import Base


class SuperUser(Base):
    __tablename__ = "superusers"

    id = Column(Integer, primary_key=True)
    name = Column(String(255),unique = True)
    password = Column(String(255))
