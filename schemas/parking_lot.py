from typing import Optional
from pydantic import BaseModel


class BaseParkingLot(BaseModel):
    lot_name : str
    address: str
    description: str
    lot_secret: str
    hourly_pay: float
    allowance_time: int
    capacity : int
    longitude : float
    lattitude : float


class CreateParkingLot(BaseParkingLot):
    pass


class ParkingLotDB(CreateParkingLot):
    id : Optional[int]

    class Config:
        orm_mode = True


class ParkinglotLogin(BaseModel):
    name : str
    secret : str
