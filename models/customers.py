from sqlalchemy import NCHAR,DateTime, Boolean, Column, Integer,String, Float, ForeignKey, Enum
from .base_model import Base


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer,primary_key=True,index=True,autoincrement = True)
    name = Column(String(255))
    email = Column(String(255),unique = True)
    gender = Column(String(1),)
    phone_number = Column(String(15),unique = True)
    vehicle_number = Column(String(15),unique = True)
    hashed_password = Column(String(255))
