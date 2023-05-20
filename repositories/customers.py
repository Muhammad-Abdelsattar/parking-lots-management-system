from typing import Any,Optional
from databases import Database
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select,insert,delete,update
from models.customers import Customer
from schemas.customer import CreateCustomer, CustomerDB
from core.database_config import get_database


class CustomersRepository:
    def __init__(self,
                 database: Database = Depends(get_database),
                 ) -> None:

        self.database= database


    async def get_customer_by_id(self,
                                 id: int):
        get_query = select(Customer).where(Customer.id == id)
        customer = await self.database.fetch_one(get_query)
        return customer


    async def get_customers_by_ids(self,
                                   ids: list[int]):
        get_query = select(Customer).where(Customer.id.in_(ids))
        customers = await self.database.fetch_all(get_query)
        return customers


    async def get_customer_by_email(self
                                    ,email: str):
        get_query = select(Customer).where(Customer.email == email)
        customer = await self.database.fetch_one(get_query)
        return customer


    async def get_customer_by_phone(self
                                    ,phone_number: str):
        get_query = select(Customer).where(Customer.phone_number == phone_number)
        customer = await self.database.fetch_one(get_query)
        return customer


    async def get_all_customers(self):
        get_query = select(Customer).all()
        customer = await self.database.fetch_all(get_query)
        return customer


    async def add_customer(self
                           ,customer: CustomerDB):
        customer_data = jsonable_encoder(customer)
        add_query = insert(Customer).values(**customer_data)
        await self.database.execute(add_query)


    async def update_customer(self,
                              id: int,
                              details: dict[str, Any]):
        update_query = update(Customer).where(Customer.id == id).values(**details)
        await self.database.execute(update_query)


    async def delete_customer(self
                              ,id: int):
        delete_query = delete(Customer).where(Customer.id == id)
        await self.database.execute(delete_query)
