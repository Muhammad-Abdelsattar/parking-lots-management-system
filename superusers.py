from sqladmin import ModelView
from typing import Any
from sqlalchemy import select,insert,update,delete
from fastapi.encoders import jsonable_encoder
from sqladmin import ModelView
from models.customers import Customer
from models.parking_lots import ParkingLot,ParkingSlot
from core.security import hash_password
from schemas.parking_slots import CreateParkingSlot
from core.database_config import get_database

class CustomersView(ModelView, model=Customer):
    name = "customer"
    name_plural = "customers"
    column_list = [Customer.name,Customer.email,Customer.gender,Customer.phone_number,Customer.vehicle_number]

    can_delete = True
    can_create = False
    can_view_details = True


# class ReservationsView(ModelView, model=OnlineReservation):
#     name = "reservation"
#     name_plural = "reservations"
#     coluumn_list = [OnlineReservation.duration,OnlineReservation.customer_id,OnlineReservation.slot_id,OnlineReservation.duration,OnlineReservation.id]
#     can_delete = True
#     can_create = False
#     can_view_details = True

async def create_slots(lot_name:str):
    database = get_database()

    get_query = select(ParkingLot).where(ParkingLot.lot_name == lot_name)
    parking_lot = await database.fetch_one(get_query)

    if(parking_lot):
        for i in range(1,parking_lot.capacity+1):
            slot = CreateParkingSlot(lot_id=parking_lot.id,
                                    slot_number=i,
                                    is_occupied=False)
            slot_data = jsonable_encoder(slot)
            add_query = insert(ParkingSlot).values(**slot_data)
            await database.execute(add_query)


class ParkinglotsView(ModelView, model=ParkingLot):
    name = "parkinglot"
    name_plural = "parkinglots"
    column_list = [ParkingLot.id,ParkingLot.lot_name,ParkingLot.address,ParkingLot.description,ParkingLot.allowance_time,ParkingLot.capacity,ParkingLot.capacity,ParkingLot.lattitude,ParkingLot.longitude]

    async def on_model_change(self, data: dict, model: Any, is_created: bool) -> None:
        data["lot_secret"] = hash_password(data["lot_secret"])
        return await super().on_model_change(data, model, is_created)
    async def after_model_change(self, data: dict, model: Any, is_created: bool) -> None:

        await create_slots(lot_name=data["lot_name"])

        return await super().after_model_change(data, model, is_created)


class ParkingSlotsView(ModelView, model=ParkingSlot):
    name = "parking slot"
    name_plural = "parking slots"
    column_list = [ParkingSlot.lot_id,ParkingSlot.slot_number,ParkingSlot.is_occupied]
