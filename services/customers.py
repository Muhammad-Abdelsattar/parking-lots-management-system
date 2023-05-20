from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException,status
from models.customers import Customer
from core.jwt import create_access_token,decode_access_token
from core.security import verify_password,hash_password
from schemas.customer import CreateCustomer,CustomerDB,BaseCustomer
from schemas.jwt import JWTSchema,EnumUserRole
from repositories.customers import CustomersRepository


class CustomersService:
    def __init__(self,
                 repo:CustomersRepository = Depends(CustomersRepository)
                 ) -> None:
        self.repo = repo


    async def signup(self,create_customer:CreateCustomer):
        customer_by_email = await self.repo.get_customer_by_email(email=create_customer.email)
        customer_by_phone = await self.repo.get_customer_by_phone(phone_number=create_customer.phone_number)

        if(customer_by_email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists."
            )

        if(customer_by_phone):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this phone number already exists."
            )

        customer = CustomerDB(name=create_customer.name,
                              email=create_customer.email,
                              phone_number=create_customer.phone_number,
                              hashed_password=hash_password(password=create_customer.password))


        await self.repo.add_customer(customer=customer)


    async def login(self,email:str,password:str):
        customer: Optional[CustomerDB] = await self._authenticate(email=email,password=password)
        if(customer):
            return {
                "access_token" : create_access_token(role = EnumUserRole.customer,
                                                     subject = customer.id),
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.")


    async def get_customer_from_token(self,
                                      token: str):
        try:
            token_data = decode_access_token(token=token)
            token_data = JWTSchema(**token_data)

            if(token_data.role == EnumUserRole.customer):
                if(token_data.expiration_date<datetime.now()):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token Expired. please login again.")

                customer = await self.repo.get_customer_by_id(id=token_data.id)
                customer = CustomerDB.from_orm(customer)
                return customer

            else:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="This action is not allowed for this type of user.")

        except :
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                )



    async def _authenticate(self,email:str,password:str) -> Optional[CustomerDB]:

        customer = await self.repo.get_customer_by_email(email=email)

        if(customer):
            customer = CustomerDB.from_orm(customer)
            if(verify_password(customer.hashed_password,password)):
                return customer

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There's no customer with the provided email address.")


    # async def get_customer(self,
    #                        id: int):
    #     customer = await self.repo.get_customer_by_id(id=id)

    #     if(customer):
    #         customer = CustomerDB.from_orm(customer)
    #         customer = CustomerInReservation(name=customer.name,
    #                                          phone_number=customer.phone_number,
    #                                          vehicle_number="1234")
    #         return customer

    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail="Customer wasn't found. It may have been deleted.")
