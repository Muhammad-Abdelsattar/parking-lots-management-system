import os
from typing import Any, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, status,HTTPException
from schemas.jwt import JWTSchema,EnumUserRole
from jose import jwt
from datetime import datetime,timedelta
from .config import get_settings


settings = get_settings()

def create_access_token(role:EnumUserRole,
                        subject: Any,
                        expires_delta: Optional[int] = None) -> str:

    if(expires_delta is not None):
        expiry_date = datetime.utcnow() + timedelta(minutes=expires_delta)

    else:
        expiry_date = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINS)

    token_data = JWTSchema(id=subject,
                           role=role,
                           expiration_date=expiry_date)

    encoded_jwt = jwt.encode(claims= jsonable_encoder(token_data),key= settings.JWT_SECRET_KEY,algorithm= settings.JWT_HASH_ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str):
    payload = jwt.decode(token=token,
                      key=settings.JWT_SECRET_KEY,
                      algorithms=settings.JWT_HASH_ALGORITHM)

    return payload



# def get_user_from_token(token: str,
#                         lots_service: ParkingLotsService = Depends(),
#                         customers_service: CustomersService = Depends()):

#     try:
#         token_data = decode_access_token(token=token)
#         token_data = JWTSchema(**token_data)

#         if(token_data.role == EnumUserRole.parkinglot):
#             if(token_data.expiration_date<datetime.now()):
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="Token Expired. please login again.")

#             lot = await self.lots_repo.get_lot_by_id(id=token_data.id)
#             lot = ParkingLotDB.from_orm(lot)
#             return lot

#         elif(token_data.role == EnumUserRole.customer):
#             if(token_data.expiration_date<datetime.now()):
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="Token Expired. please login again.")

#             lot = await self.lots_repo.get_lot_by_id(id=token_data.id)
#             lot = ParkingLotDB.from_orm(lot)
#             return lot

        # elif(token_data.role == EnumUserRole.parkinglot):
        #     if(token_data.expiration_date<datetime.now()):
        #         raise HTTPException(
        #             status_code=status.HTTP_401_UNAUTHORIZED,
        #             detail="Token Expired. please login again.")

        #     lot = await self.lots_repo.get_lot_by_id(id=token_data.id)
        #     lot = ParkingLotDB.from_orm(lot)
        #     return lot

#         else:
#             raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
#                                 detail="This action is not allowed for this type of user.")

#     except :
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Token is not valid."
#             )
