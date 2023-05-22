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
from pyngrok import ngrok


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)



port = 9000
ngrok_tunnel = ngrok.connect(port)

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


@server.get('/')
def index():
    pass
    return {'Public URL': ngrok_tunnel.public_url}

# @server.get('/add_customers')
# async def add_customers(customers_service: CustomersService= Depends(CustomersService)):
#     for customer in dumb_customers:
#         await customers_service.signup(create_customer=customer)

# @server.get('/add_lots')
# async def add_lots(lots_repo: ParkinglotsRepository= Depends(ParkinglotsRepository)):
#     for lot in dumb_lots:
#         await lots_repo.add_lot(parking_lot=lot)

# def commons(start:int,end:int):
#     return start+end


# @server.get('/add')
# def add(commons:int =Depends(commons)):
#     return commons
