from datetime import datetime
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, EmailStr


class EnumGender(str,Enum):
    male = 'm'
    female = 'f'


class BaseCustomer(BaseModel):
    name : str
    email : EmailStr
    phone_number : str
    vehicle_number: str
    gender: EnumGender


class CustomerLogin(BaseModel):
    email : EmailStr
    password : str


class CreateCustomer(BaseCustomer):
    password : str


class UpdateCustomer(CreateCustomer):
    pass


class CustomerDB(BaseCustomer):
    id : Optional[int] = None
    hashed_password : str

    class Config:
        orm_mode = True
