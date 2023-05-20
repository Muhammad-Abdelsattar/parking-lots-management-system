from typing import Any,Optional
from databases import Database
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select,insert,delete,update
from core.database_config import get_database
from schemas.reservation import *
from models.reservations import *


class OnlineReservationsRepository:
    def __init__(self,
                 database: Database = Depends(get_database),
                 ) -> None:

        self.database= database


    async def get_reservation_by_id(self
                                    ,id : int):
        get_query = select(OnlineReservation).where(OnlineReservation.id == id)
        reservation = await self.database.fetch_one(get_query)
        return reservation


    async def get_all_reservations(self):
        get_query = select(OnlineReservation).all()
        reservation = await self.database.fetch_all(get_query)
        return reservation


    async def add_reservation(self,
                              reservation:OnlineReservationDB):
        reservation_data = jsonable_encoder(reservation)
        reservation_data["start_time"] = reservation.start_time
        add_query = insert(OnlineReservation).values(**reservation_data)
        await self.database.execute(add_query)


    async def update_reservation(self,id:int,
                                 details:dict[str, Any]):
        update_query = update(OnlineReservation).where(OnlineReservation.id == id).values(details)
        await self.database.execute(update_query)


    async def delete_reservation(self,
                                      id:int):
        delete_query = delete(OnlineReservation).where(OnlineReservation.id == id)
        await self.database.execute(delete_query)


    async def get_customer_reservations(self,
                                        limit:Optional[int],
                                        offset:Optional[int],
                                        customer_id:int,
                                        state:Optional[EnumReservationState] = None):
        if(limit and offset):
            if(state):
                get_query = select(OnlineReservation).\
                    where(OnlineReservation.customer_id == customer_id).\
                    where(OnlineReservation.state == state).\
                    slice(offset,offset+limit)

            else:
                get_query = select(OnlineReservation).\
                    where(OnlineReservation.customer_id== customer_id).\
                    slice(offset,offset+limit)
        else:
            if(state):
                get_query = select(OnlineReservation).\
                    where(OnlineReservation.customer_id == customer_id).\
                    where(OnlineReservation.state == state)

            else:
                get_query = select(OnlineReservation).\
                    where(OnlineReservation.customer_id== customer_id)


        reservations = await self.database.fetch_all(get_query)

        return reservations


    async def get_reservations_by_slots_ids(self,
                                            limit: int,
                                            offset: int,
                                            slots_ids:list[int],
                                            state:Optional[EnumReservationState] = None):

        if(state):
            get_query = select(OnlineReservation).\
                where(OnlineReservation.slot_id.in_(slots_ids)).\
                where(OnlineReservation.state == state).\
                slice(offset,offset+limit)
        else:
            get_query = select(OnlineReservation).\
                where(OnlineReservation.slot_id.in_(slots_ids)).\
                slice(offset,offset+limit)

        reservations = await self.database.fetch_all(get_query)

        return reservations
