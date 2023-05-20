from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.customer import *
from services.customers import CustomersService
from .common import get_current_user


router = APIRouter(
    prefix="/customers",
    tags=["customers"]
    )


@router.get('/me',
            status_code=status.HTTP_200_OK,
            response_model=BaseCustomer)
async def get_customer_profile(customer: CustomerDB = Depends(get_current_user),
                               customers_service: CustomersService = Depends()):

    customer_profile = await customers_service.get_customer(id=customer.id)

    return customer_profile


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
