from datetime import datetime
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, EmailStr


class EnumUserRole(str,Enum):
    customer = "customer"
    parkinglot = "parkinglot"


class JWTSchema(BaseModel):
    id: int
    role: EnumUserRole
    expiration_date: datetime
