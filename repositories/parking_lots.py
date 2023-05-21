from enum import Enum
from typing import Any
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, insert, update, delete
from models.parking_lots import ParkingLot
from schemas.parking_lot import *
from core.database_config import get_database


class EnumOrderBy(str,Enum):
    hourly_pay = "hourly_pay"
    allowance_time = "allowance_time"
    capacity = "capacity"


class EnumOrder(str,Enum):
    ascending = "accending"
    descending = "descending"


class ParkinglotsRepository:
    def __init__(self,
                 database = Depends(get_database),
                 ) -> None:

        self.database = database


    async def get_lot_by_id(self
                             ,id : int):
        get_query = select(ParkingLot).where(ParkingLot.id == id)
        lot = await self.database.fetch_one(get_query)
        return lot


    async def get_lot_by_name(self,
                              name:str):
        get_query = select(ParkingLot).where(ParkingLot.lot_name == name)
        lot = await self.database.fetch_one(get_query)
        return lot


    async def get_all_lots(self):
        get_query = select(ParkingLot)
        lots = await self.database.fetch_all(get_query)
        return lots


    async def get_lots(self,
                       limit: Optional[int] = None,
                       offset: Optional[int] = None,
                       order_by:Optional[EnumOrderBy] = None,
                       order:Optional[EnumOrder] = None,
                       ):

        print(limit + offset)

        if(order_by):
            if(order == EnumOrder.ascending):
                lots = await self.get_lots_ascending(order_by=order_by,
                                        limit=limit,
                                        offset=offset)

            elif(order == EnumOrder.descending):
                lots = await self.get_lots_descending(order_by=order_by,
                                        limit=limit,
                                        offset=offset)

            else:
                lots = await self.get_lots_ascending(order_by=order_by,
                                        limit=limit,
                                        offset=offset)

        else:
            lots = await self.get_lots_ascending(order_by=EnumOrderBy.hourly_pay,
                                    limit=limit,
                                    offset=offset)

        return lots


    async def get_lots_ascending(self,
                                 order_by:EnumOrderBy,
                                 limit: Optional[int] = None,
                                 offset: Optional[int] = None):

        column = getattr(ParkingLot,order_by)

        if(limit is not None and offset is not None):
            get_query = select(ParkingLot).\
                order_by(column.asc()).\
                slice(offset,limit+offset)

        else:
            get_query = select(ParkingLot).\
                order_by(column.asc())

        lots = await self.database.fetch_all(get_query)

        return lots


    async def get_lots_descending(self,
                                  order_by:EnumOrderBy,
                                 limit: Optional[int] = None,
                                 offset: Optional[int] = None):

        column = getattr(ParkingLot,order_by)

        if(limit is not None and offset is not None):
            get_query = select(ParkingLot).\
                order_by(column.desc()).\
                slice(offset,limit+offset)
        else:
            get_query = select(ParkingLot).\
                order_by(column.desc())

        lots = await self.database.fetch_all(get_query)

        return lots


    async def get_highest_cost_lots(self,
                                  limit: int,
                                  offset: int):
        get_query = select(ParkingLot).\
            order_by(ParkingLot.hourly_pay.desc()).\
            slice(offset,limit+offset)

        lots = await self.database.fetch_all(get_query)
        return lots


    async def get_highest_allowance_lots(self,
                                  limit: int,
                                  offset: int):
        get_query = select(ParkingLot).\
            order_by(ParkingLot.allowance_time.desc()).\
            slice(offset,limit+offset)

        lots = await self.database.fetch_all(get_query)
        return lots


    async def get_least_allowance_lots(self,
                                  limit: int,
                                  offset: int):
        get_query = select(ParkingLot).\
            order_by(ParkingLot.allowance_time).\
            slice(offset,limit+offset)

        lots = await self.database.fetch_all(get_query)
        return lots


    async def get_highest_capacity_lots(self,
                                  limit: int,
                                  offset: int):
        get_query = select(ParkingLot).\
            order_by(ParkingLot.capacity.desc()).\
            slice(offset,limit+offset)

        lots = await self.database.fetch_all(get_query)
        return lots


    async def get_least_capacity_lots(self,
                                  limit: int,
                                  offset: int):
        get_query = select(ParkingLot).\
            order_by(ParkingLot.capacity).\
            slice(offset,limit+offset)

        lots = await self.database.fetch_all(get_query)
        return lots


    async def add_lot(self,
                      parking_lot: ParkingLotDB):

        parking_lot_data = jsonable_encoder(parking_lot)
        add_query = insert(ParkingLot).values(**parking_lot_data)
        await self.database.execute(add_query)


    async def update_lot(self,
                          id:int,
                          details:dict[str, Any]):

        update_query = update(ParkingLot).where(ParkingLot.id == id).values(details)
        await self.database.execute(update_query)


    async def delete_lot(self,
                          id:int):
        delete_query = delete(ParkingLot).where(ParkingLot.id == id)
        await self.database.execute(delete_query)
