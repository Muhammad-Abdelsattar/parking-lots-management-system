from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, EmailStr


class BaseCustomer(BaseModel):
    name : str
    email : EmailStr
    phone_number : str


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
