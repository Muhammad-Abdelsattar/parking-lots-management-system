from sqlalchemy import DateTime, Boolean, Column, Integer,String, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from .base_model import Base
import enum


class EnumParkingLotType(enum.Enum):
    single_level_garage = 1
    multi_level_garage = 2
    underground_garage = 3
    automated_garage = 4


class ParkingLotType(Base):
    __tablename__ = "parkinglot_types"

    id = Column(Integer,primary_key=True,index=True,autoincrement = True)
    lot_type = Column(Enum(EnumParkingLotType))


class ParkingLot(Base):
    __tablename__ = 'parkinglots'

    id = Column(Integer,primary_key=True,index=True,autoincrement = True)
    lot_name = Column(String(255),unique = True)
    picture = Column(String(255))
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
