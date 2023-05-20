from datetime import datetime
import enum
from typing import Optional, Union
from pydantic import BaseModel, EmailStr, validator
from models.reservations import EnumReservationState


class BaseReservation(BaseModel):
    duration: int

    @validator("duration")
    def duration_between_1_24(cls, value):
        if(value < 1 or value > 24):
            raise ValueError("Duration must be between (1 : 24) hours.")
        return value


class OnlineReservationData(BaseReservation):
    customer_id:int


class OnlineReservationDB(OnlineReservationData):
    id: Optional[int]
    start_time: datetime
    state: EnumReservationState
    total_pay: float
    slot_id: int

    class Config:
        orm_mode = True


class CustomerInReservation(BaseModel):
    customer_name: str
    phone_number: str
    vehicle_number: str


class MakeReservation(BaseReservation):
    lot_id: int


class LotReservationAbstract(BaseReservation):
    id: int
    state: EnumReservationState
    customer_name: str


class LotReservationDetails(BaseReservation):
    id: int
    start_time: datetime
    state: EnumReservationState
    total_pay: float
    phone_number: str
    customer_name: str
    vehicle_number: str


class CustomerReservationDetails(BaseReservation):
    id: int
    start_time: datetime
    state: EnumReservationState
    total_pay: float
    lot_name: str


class CustomerReservationAbstract(BaseReservation):
    id: int
    state: EnumReservationState
    lot_name: str
