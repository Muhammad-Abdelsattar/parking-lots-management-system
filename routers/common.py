from fastapi import  Header, Query, status, Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from services.parking_lots import ParkingLotsService
from services.customers import CustomersService


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/customers/login",
    scheme_name="CustomerLogin"
)



class PaginatedParams:
    def __init__(self,
                 page: int = Query(1,ge=1),
                 per_page: int = Query(5,ge=0)) -> None:

        self.offset = (page - 1) * per_page
        self.limit = per_page



async def get_current_user(authorization: str = Header(default="Bearer"),
                           customers_service: CustomersService = Depends()):

    auth_type_token = authorization.split(' ')

    if(len(auth_type_token)>1):
        token = auth_type_token[1]
    else:
        token = authorization

    return await customers_service.get_customer_from_token(token=token)


async def get_current_parkinglot(authorization: str = Header(None),
                           lots_service: ParkingLotsService = Depends()):

    return await lots_service.get_lot_from_token(token=authorization)
