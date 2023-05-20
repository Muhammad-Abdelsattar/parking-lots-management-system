from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Depends
from models.base_model import init_models
from routers.customers import router as customers_router
from routers.reservations import router as reservations_router
from routers.parking_lots import router as lots_router
from fastapi.security import OAuth2PasswordBearer
from core.config import get_settings
from core.database_config import get_database,get_test_database

from services.customers import CustomersService
from repositories.parking_lots import ParkinglotsRepository
from fake_data import *


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)



server = FastAPI()
server.include_router(customers_router)
server.include_router(reservations_router)
server.include_router(lots_router)

settings = get_settings()


@server.on_event("startup")
async def startup():
    print("inside startup")
    init_models()
    await get_database().connect()


@server.on_event("shutdown")
async def shutdown():
    await get_database().disconnect()
