from datetime import datetime
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, EmailStr


class Superuser(BaseModel):
    name: str
    password: str


class SuperuserDB(BaseModel):
    id : Optional[int] = None
    name: str
    password : str

    class Config:
        orm_mode = True
