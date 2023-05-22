from typing import Any,Optional
from databases import Database
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select,insert,delete,update
from models.superuser import *
from schemas.superuser import *
from core.database_config import get_database


class SuperusersRepository:
    def __init__(self,
                 database: Database =get_database(),
                 ) -> None:

        self.database= database


    async def get_superuser_by_id(self,
                                 id: int):
        get_query = select(SuperUser).where(SuperUser.id == id)
        super_user = await self.database.fetch_one(get_query)
        return super_user


    async def get_superusers_by_ids(self,
                                   ids: list[int]):
        get_query = select(SuperUser).where(SuperUser.id.in_(ids))
        super_users = await self.database.fetch_all(get_query)
        return super_users


    async def get_superuser_by_name(self
                                    ,name: str):
        get_query = select(SuperUser).where(SuperUser.name == name)
        super_user = await self.database.fetch_one(get_query)
        return super_user


    async def get_all_superusers(self):
        get_query = select(SuperUser).all()
        super_user = await self.database.fetch_all(get_query)
        return super_user


    async def add_superuser(self
                            ,super_user: SuperuserDB):
        superuser_data = jsonable_encoder(super_user)
        add_query = insert(SuperUser).values(**superuser_data)
        await self.database.execute(add_query)


    async def update_superuser(self,
                              id: int,
                              details: dict[str, Any]):
        update_query = update(SuperUser).where(SuperUser.id == id).values(**details)
        await self.database.execute(update_query)


    async def delete_superuser(self
                              ,id: int):
        delete_query = delete(SuperUser).where(SuperUser.id == id)
        await self.database.execute(delete_query)
