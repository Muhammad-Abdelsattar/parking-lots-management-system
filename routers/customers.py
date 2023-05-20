from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.customer import *
from services.customers import CustomersService


router = APIRouter(
    prefix="/customers",
    tags=["customers"]
    )


@router.post('/login',status_code=status.HTTP_200_OK)
async def login(customer_login: CustomerLogin,
          customers_service: CustomersService = Depends(CustomersService),
          ):
    token = (await customers_service.login(email=customer_login.email,
                                           password=customer_login.password))["access_token"]
    return token


@router.post('/register',status_code=status.HTTP_201_CREATED)
async def register(customer: CreateCustomer,
                   customers_service: CustomersService = Depends(CustomersService)
                   ):
    await customers_service.signup(create_customer=customer)
