from typing import Any
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select,insert, update, delete
from models.parking_lots import ParkingSlot
from schemas.parking_slots import *
from core.database_config import get_database


class ParkingSlotsRepository:
    def __init__(self,
                 database = Depends(get_database),
                 ) -> None:

        self.database = database


    async def get_slot_by_id(self
                             ,id : int):

        get_query = select(ParkingSlot).where(ParkingSlot.id == id)
        slot = await self.database.fetch_one(get_query)
        return slot


    async def get_first_available_slot_in_lot(self,
                                              lot_id: int):
        get_query = select(ParkingSlot).where(ParkingSlot.lot_id == lot_id).where(ParkingSlot.is_occupied == False)
        slot = await self.database.fetch_one(get_query)
        return slot


    async def get_slot_by_number_and_lot_id(self,
                                 lot_id: int,
                                 slot_number : int):

        get_query = select(ParkingSlot)\
            .where(ParkingSlot.lot_id == lot_id)\
            .where(ParkingSlot.slot_number == slot_number)

        slot = await self.database.fetch_one(get_query)
        return slot


    async def get_all_slots(self):

        get_query = select(ParkingSlot)
        slot = await self.database.fetch_all(get_query)
        return slot


    async def get_all_parkinglot_slots(self,
                                       lot_id: int):

        get_query = select(ParkingSlot).where(ParkingSlot.lot_id == lot_id)
        slots = await self.database.fetch_all(get_query)
        return slots


    async def get_parkinglot_free_slots(self,
                                       lot_id: int):

        get_query = select(ParkingSlot).where(ParkingSlot.lot_id == lot_id).where(ParkingSlot.is_occupied == False)
        slots = await self.database.fetch_all(get_query)
        return slots


    async def add_slot(self,
                       slot: CreateParkingSlot):

        slot_data = jsonable_encoder(slot)
        add_query = insert(ParkingSlot).values(**slot_data)
        await self.database.execute(add_query)


    # async def add_slots(self,
    #                     slots: list[CreateParkingSlot]):
    #     slots_data = [jsonable_encoder(slot) for slot in slots]
    #     print(slots_data)
    #     add_query = insert(ParkingSlot).values(**slots_data)
    #     await self.database.execute_many(add_query)


    async def update_slot(self,
                          id:int,
                          details:dict[str, Any]):

        update_query = update(ParkingSlot).where(ParkingSlot.id == id).values(details)
        await self.database.execute(update_query)


    async def delete_slot(self,
                          id:int):

        delete_query = delete(ParkingSlot).where(ParkingSlot.id == id)
        await self.database.execute(delete_query)
