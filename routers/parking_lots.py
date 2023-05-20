from fastapi import APIRouter, status, Depends

from repositories.parking_lots import EnumOrderBy, EnumOrder
from .common import PaginatedParams
from schemas.parking_lot import *
from services.parking_lots import ParkingLotsService

router = APIRouter(
    prefix="/parking-lots",
    tags=["parking lots"]
    )


@router.post('/login',status_code=status.HTTP_200_OK)
async def login(lot_login: ParkinglotLogin,
          lots_service: ParkingLotsService = Depends(),
          ):
    token = (await lots_service.login(lot_name=lot_login.name,
                                           secret=lot_login.secret))["access_token"]
    return token


@router.post('/',status_code=status.HTTP_201_CREATED)
async def add_parking_lot(parking_lot: CreateParkingLot,
                          lots_service: ParkingLotsService=Depends(ParkingLotsService)):
    await lots_service.add_parkinglot(parking_lot=parking_lot)


@router.get('/{id}',status_code=status.HTTP_200_OK)
async def get_lot(id:int,
                       lots_service: ParkingLotsService=Depends(ParkingLotsService)):
    return await lots_service.get_detailed_parkinglot_data(lot_id=id)


@router.get('/',status_code=status.HTTP_200_OK,)
async def get_lots(order_by:Optional[EnumOrderBy] = None,
                   order:Optional[EnumOrder] = None,
                   pagination:PaginatedParams = Depends(),
                   lots_service: ParkingLotsService=Depends(ParkingLotsService)):

    return await lots_service.get_abstract_parkinglots_data(order_by=order_by,
                                              order=order,
                                              limit=pagination.limit,
                                              offset=pagination.offset)



# @router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
# async def delete_parkinglot(id:int,
#                             lots_service: ParkingLotsService=Depends(ParkingLotsService)):

#     await lots_service.remove_parkinglot(lot_id=id)
