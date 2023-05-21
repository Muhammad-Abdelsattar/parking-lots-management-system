from fastapi import APIRouter, HTTPException, Request, status, Depends,Header
from services.customers import CustomersService
from schemas.parking_lot import ParkingLotDB
from schemas.reservation import *
from services.reervations import ReservationsService
from schemas.customer import CustomerDB
from .common import PaginatedParams, get_current_user, get_current_parkinglot, get_user


router = APIRouter(
    prefix="/reservations",
    tags=["reservations"]
    )


@router.post("/",
             status_code=status.HTTP_201_CREATED)
async def make_reservation(reservation: MakeReservation,
                           reservations_service: ReservationsService = Depends(),
                           customer: CustomerDB = Depends(get_current_user),
                           ):

    reservation_data = OnlineReservationData(duration=reservation.duration,
                                             customer_id=customer.id)

    await reservations_service.make_reservation(lot_id=reservation.lot_id,
                                                reservation_data =reservation_data)

@router.get('/',
            status_code=status.HTTP_200_OK,
            response_model=list[Union[CustomerReservationAbstract,LotReservationAbstract]])
async def get_reservations(state: Optional[EnumReservationState] = None,
                           user = Depends(get_user),
                           pagination: PaginatedParams = Depends(),
                           reservations_service: ReservationsService = Depends()):

    reservations = await reservations_service.get_reservations(user_role=user["role"],
                                                               user_id=user["user"].id,
                                                               limit=pagination.limit,
                                                               offset=pagination.offset,
                                                               state=state
                                                               )
    return reservations


@router.get('/{reservation_id}',
            status_code=status.HTTP_200_OK,
            response_model=list[Union[CustomerReservationAbstract,LotReservationAbstract]])
async def get_reservation_details(reservation_id:int,
                                  user = Depends(get_user),
                                  reservations_service: ReservationsService = Depends()):

    reservation = await reservations_service.get_reservation_details(user_role=user["role"],
                                                                      user_id=user["user"].id,
                                                                      reservation_id=reservation_id
                                                                      )
    return reservation


@router.get("/customer",
            status_code=status.HTTP_200_OK,
            response_model=list[CustomerReservationAbstract])
async def get_customer_reservations(state: Optional[EnumReservationState] = None,
                                    pagination: PaginatedParams = Depends(),
                                    reservations_service: ReservationsService = Depends(),
                                    customer: CustomerDB = Depends(get_current_user),
                                    ):

    reservations = await reservations_service.get_customer_abstract_online_reservations(customer_id=customer.id,
                                                                               limit=pagination.limit,
                                                                               offset=pagination.offset,
                                                                               state = state)
    return reservations


@router.get('/customer/{reservation_id}',
            status_code=status.HTTP_200_OK,
            response_model=CustomerReservationDetails)
async def get_customer_reservation_details(reservation_id:int,
                                           customer: CustomerDB = Depends(get_current_user),
                                           reservations_service: ReservationsService = Depends(),
                                           ):

    reservation = await reservations_service.get_customer_detailed_reservation(reservation_id = reservation_id,
                                                                               customer_id=customer.id)
    return reservation


@router.get("/parking-lot/",
            status_code=status.HTTP_200_OK,
            response_model=list[Optional[LotReservationAbstract]])
async def get_parkinglot_reservations(state: Optional[EnumReservationState] = None,
                                      pagination: PaginatedParams = Depends(),
                                      reservations_service: ReservationsService = Depends(),
                                      lot : ParkingLotDB = Depends(get_current_parkinglot)
                                      ):

    reservations = await reservations_service.get_parkinglot_abstract_online_reservations(lot_id=lot.id,
                                                                                          limit=pagination.limit,
                                                                                          offset=pagination.offset,
                                                                                          state = state)
    return reservations


@router.get('/parking-lot/{reservation_id}',
            status_code=status.HTTP_200_OK,
            response_model=LotReservationDetails)
async def get_parkinglot_reservation_details(reservation_id:int,
                                  lot: ParkingLotDB = Depends(get_current_parkinglot),
                                  reservations_service: ReservationsService = Depends(),
                                  ):

    reservation = await reservations_service.get_parkinglot_detailed_reservation(reservation_id = reservation_id,
                                                                                 lot_id=lot.id)
    return reservation


@router.post("/customer/{reservation_id}/cancel",
             status_code=status.HTTP_200_OK)
async def customer_cancel_reservation(reservation_id: int,
                           reservations_service: ReservationsService = Depends(),
                           customer: CustomerDB = Depends(get_current_user),
                           ):

    await reservations_service.customer_cancel_online_reservation(customer_id=customer.id,
                                                           reservation_id=reservation_id)


@router.post("/parking-lot/{reservation_id}/cancel",
             status_code=status.HTTP_200_OK)
async def parkinglot_cancel_reservation(reservation_id: int,
                                        reservations_service: ReservationsService = Depends(ReservationsService),
                                        lot : ParkingLotDB = Depends(get_current_parkinglot)
                                        ):

    await reservations_service.parkinglot_cancel_online_reservation(lot_id=lot.id,
                                                                    reservation_id=reservation_id)


@router.post("/parking-lot/{reservation_id}/activate",
             status_code=status.HTTP_200_OK)
async def parkinglot_activate_reservation(reservation_id: int,
                                          reservations_service: ReservationsService = Depends(ReservationsService),
                                          lot : ParkingLotDB = Depends(get_current_parkinglot)
                                          ):
    await reservations_service.activate_reservation(lot_id=lot.id,
                                                    reservation_id=reservation_id)
