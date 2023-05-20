from sqlalchemy import DateTime, Boolean, Column, Integer,String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base_model import Base
import enum


class EnumReservationState(str,enum.Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    canceled_by_customer = "cancelled by customer"
    canceled_by_operator = "cancelled by operator"


class OnlineReservation(Base):
    __tablename__ = 'online_reservations'

    id = Column(Integer,primary_key=True,index=True,autoincrement = True)
    slot_id = Column(Integer,ForeignKey("parking_slots.id"))
    customer_id = Column(Integer,ForeignKey("customers.id"))
    start_time = Column(DateTime)
    duration = Column(Integer)
    total_pay = Column(Float)
    state = Column(Enum(EnumReservationState))
