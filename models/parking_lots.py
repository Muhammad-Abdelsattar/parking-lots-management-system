from sqlalchemy import DateTime, Boolean, Column, Integer,String, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from .base_model import Base
import enum


class ParkingLot(Base):
    __tablename__ = 'parkinglots'

    id = Column(Integer,primary_key=True,index=True,autoincrement = True)
    lot_name = Column(String(255),unique = True)
    address = Column(String(255))
    description = Column(Text)
    lot_secret = Column(String(255))
    capacity = Column(Integer)
    hourly_pay = Column(Float)
    allowance_time = Column(Integer)
    longitude = Column(Float)
    lattitude = Column(Float)


class ParkingSlot(Base):
    __tablename__ = 'parking_slots'

    id = Column(Integer,primary_key=True,index=True,autoincrement = True)
    lot_id = Column(Integer,ForeignKey("parkinglots.id"))

    slot_number = Column(Integer)
    is_occupied = Column(Boolean)
