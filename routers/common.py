from fastapi import  Header, Query, status, Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from repositories import parking_lots
from services.parking_lots import ParkingLotsService
from services.customers import CustomersService
from core.jwt import *
from schemas.jwt import *
from schemas.customer import CustomerDB
from schemas.parking_lot import ParkingLotDB


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/customers/login",
    scheme_name="CustomerLogin"
)



class PaginatedParams:
    def __init__(self,
                 page: Optional[int],
                 per_page: Optional[int])  -> None:

        if(page and per_page):
            self.offset = (page - 1) * per_page
            self.limit = per_page
        else:
            self.offset = None
            self.limit = None



async def get_current_user(security: str = Header(default="Bearer"),
                           customers_service: CustomersService = Depends()):

    auth_type_token = security.split(' ')

    if(len(auth_type_token)>1):
        token = auth_type_token[1]
    else:
        token = security

    return await customers_service.get_customer_from_token(token=token)


async def get_current_parkinglot(security: str = Header(None),
                           lots_service: ParkingLotsService = Depends()):

    return await lots_service.get_lot_from_token(token=security)


async def get_user(security: str = Header(None),
                   lots_service: ParkingLotsService = Depends(),
                   customers_service: CustomersService = Depends()):

    user = {}
    try:
        token_data = decode_access_token(token=security)
        token_data = JWTSchema(**token_data)

        if(token_data.role == EnumUserRole.parkinglot):
            if(token_data.expiration_date<datetime.now()):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token Expired. please login again.")

            lot = await lots_service.lots_repo.get_lot_by_id(id=token_data.id)
            lot = ParkingLotDB.from_orm(lot)
            user["user":lot,
                 "role":token_data.role]
            return user

        elif(token_data.role == EnumUserRole.customer):
            if(token_data.expiration_date<datetime.now()):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token Expired. please login again.")

            customer = await customers_service.repo.get_customer_by_id(id=token_data.id)
            customer = CustomerDB.from_orm(customer)

            user["user"] = customer
            user["role"] = token_data.role
            return user

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not valid."
                )


    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not valid."
            )
