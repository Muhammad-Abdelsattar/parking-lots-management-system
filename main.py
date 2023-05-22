from typing import Optional,Any
from fastapi import FastAPI
from sqladmin import Admin,ModelView
from models.base_model import init_models
from models.customers import Customer
from models.parking_lots import ParkingLot,ParkingSlot
from schemas.parking_slots import CreateParkingSlot
from repositories.parking_slots import ParkingSlotsRepository
from routers.customers import router as customers_router
from routers.reservations import router as reservations_router
from routers.parking_lots import router as lots_router
from core.config import get_settings
from core.database_config import get_database,engine
from services.superusers import AdminsService
from repositories.parking_lots import ParkinglotsRepository
from superusers import CustomersView,ParkinglotsView,ParkingSlotsView


server = FastAPI()
server.include_router(customers_router)
server.include_router(reservations_router)
server.include_router(lots_router)

settings = get_settings()

authentication_backend = AdminsService(secret_key="1234")

admin = Admin(app=server,engine=engine,authentication_backend=authentication_backend)

admin.add_view(CustomersView)
# admin.add_view(ReservationsView)
admin.add_view(ParkinglotsView)
admin.add_view(ParkingSlotsView)


@server.on_event("startup")
async def startup():
    init_models()
    await get_database().connect()


@server.on_event("shutdown")
async def shutdown():
    await get_database().disconnect()
