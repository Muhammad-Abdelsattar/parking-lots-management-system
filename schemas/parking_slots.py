from typing import Optional
from pydantic import BaseModel


class BaseParkingSlot(BaseModel):
    lot_id: int
    slot_number: int
    is_occupied: bool


class CreateParkingSlot(BaseParkingSlot):
    pass


class ParkingSlotDB(CreateParkingSlot):
    id : Optional[int]

    class Config:
        orm_mode = True
