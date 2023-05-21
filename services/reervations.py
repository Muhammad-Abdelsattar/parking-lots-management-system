from datetime import datetime,timedelta
from enum import Enum
from typing import Optional,Union
from fastapi import Depends, HTTPException,status
from sqlalchemy import select
from models.reservations import OnlineReservation
from schemas.jwt import EnumUserRole
from schemas.customer import CustomerDB
from schemas.parking_slots import *
from schemas.parking_lot import *
from schemas.reservation import *
from repositories.customers import CustomersRepository
from repositories.reservations import *
from repositories.parking_slots import ParkingSlotsRepository
from repositories.parking_lots import ParkinglotsRepository


class EnumReservationType(str,Enum):
    online = "online"
    offline = "offline"


class ReservationsService:
    def __init__(self,
                 online_reservations_repo:OnlineReservationsRepository = Depends(),
                 slots_repo:ParkingSlotsRepository = Depends(),
                 lots_repo:ParkinglotsRepository = Depends(),
                 customers_repo:CustomersRepository = Depends(),
                ) -> None :

        self.online_reservations_repo = online_reservations_repo
        self.slots_repo = slots_repo
        self.lots_repo = lots_repo
        self.customers_repo = customers_repo


    async def make_reservation(self,
                               lot_id: int,
                               reservation_data: OnlineReservationData,
                               ):


        if(reservation_data.duration<1):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="The duration can't be less than one hour.")

        customer_reservations = await self.get_customer_abstract_online_reservations(customer_id=reservation_data.customer_id,
                                                                            state=EnumReservationState.pending)

        if(customer_reservations):
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail="You can possess only one pending reservation.")

        lot = await self.lots_repo.get_lot_by_id(id = lot_id)

        if(lot):
            lot = ParkingLotDB.from_orm(lot)
            slot = await self.slots_repo.get_first_available_slot_in_lot(lot_id=lot.id)

            if(slot):
                slot = ParkingSlotDB.from_orm(slot)
                if(slot.is_occupied):
                    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                        detail="The slot you're trying to reserve is currently occupied. Kindly make reservation again.")

                else:
                    total_pay = lot.hourly_pay * reservation_data.duration
                    reservation = OnlineReservationDB(start_time=datetime.utcnow() + timedelta(minutes=lot.allowance_time),
                                                    duration=reservation_data.duration,
                                                    slot_id=slot.id,
                                                    total_pay=total_pay,
                                                    state=EnumReservationState.pending,
                                                    customer_id=reservation_data.customer_id,
                                                    )

                    await self.online_reservations_repo.add_reservation(reservation=reservation)
                    await self.slots_repo.update_slot(id=slot.id,
                                                      details={"is_occupied":True})

            else:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                    detail="No available parking spaces in this parking lot.")

        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="Parking  lot doesn't exist.")


    async def activate_reservation(self,
                                   lot_id: int,
                                   reservation_id: int,
                                  ):

        reservation = await self.online_reservations_repo.get_reservation_by_id(id=reservation_id)

        if(reservation):
            reservation = OnlineReservationDB.from_orm(reservation)
            slot = await self.slots_repo.get_slot_by_id(reservation.slot_id)
            if(slot):
                slot = ParkingSlotDB.from_orm(slot)
                if(slot.lot_id == lot_id):
                    if(reservation.state is not EnumReservationState.pending):
                        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                            detail="Can't activate a reservation that is not in the pending state.")

                    await self.online_reservations_repo.update_reservation(id = reservation_id,
                                                details={"state" :EnumReservationState.active,
                                                         "start_time" :datetime.now()
                                                })
                else:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="This parking lot doesn't posses this reservation.")
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Parking slot not found.")

        else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Reservation not found.")


    async def customer_cancel_online_reservation(self,
                                          customer_id:int,
                                          reservation_id:int
                                          ):

        reservation = await self.online_reservations_repo.get_reservation_by_id(id=reservation_id)
        if(reservation):
            reservation = OnlineReservationDB.from_orm(reservation)
            if(reservation.customer_id == customer_id):
                if(reservation.state is not EnumReservationState.pending):
                    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                        detail="Can't cancel a reservation that is not in the pending state.")

                await self._update_reservation_state(reservation_id=reservation_id,
                                                    state=EnumReservationState.canceled_by_customer)
                await self.slots_repo.update_slot(id=reservation.slot_id,
                                                  details={"is_occupied":False})

            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="This customer doesn't posses this reservation.")

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Reservation not found.")


    async def parkinglot_cancel_online_reservation(self,
                                          lot_id:int,
                                          reservation_id:int
                                          ):

        reservation = await self.online_reservations_repo.get_reservation_by_id(id=reservation_id)

        if(reservation):
            reservation = OnlineReservationDB.from_orm(reservation)
            slot = await self.slots_repo.get_slot_by_id(reservation.slot_id)
            if(slot):
                slot = ParkingSlotDB.from_orm(slot)
                if(slot.lot_id == lot_id):
                    if(reservation.state is not EnumReservationState.pending):
                        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                            detail="Can't cancel a reservation that is not in the pending state.")

                    elif(reservation.state == EnumReservationState.pending
                         and datetime.now() > reservation.start_time):

                        await self._update_reservation_state(reservation_id=reservation_id,
                                                            state=EnumReservationState.canceled_by_operator)
                        await self.slots_repo.update_slot(id=reservation.slot_id,
                                                        details={"is_occupied":False})

                    elif(reservation.state == EnumReservationState.pending
                         and datetime.now() <= reservation.start_time):
                        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                            detail="Can't cancel a reservation before its allowance time ends.")

                else:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="This parking lot doesn't posses this reservation.")
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Parking slot not found.")

        else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Reservation not found.")


    async def end_online_reservation(self,
                              reservation_id: int):
        reservation = await self.online_reservations_repo.get_reservation_by_id(id=reservation_id)
        if(reservation):
            reservation = OnlineReservationDB.from_orm(reservation)
            if(reservation.state is EnumReservationState.active
               and reservation.start_time + timedelta(hours=reservation.duration) < datetime.now()):
                await self._update_reservation_state(reservation_id=reservation_id,
                                                    state=EnumReservationState.expired)

            else:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="Can't end the reservations at this state and time.")


    async def get_reservations(self,
                               user_role: EnumUserRole,
                               user_id: int,
                               limit: Optional[int] = None,
                               offset: Optional[int] = None,
                               state: Optional[EnumReservationState] = None,
                               ):
        if(user_role == EnumUserRole.customer):
            return await self.get_customer_abstract_online_reservations(customer_id=user_id,
                                                                        limit=limit,
                                                                        offset=offset,
                                                                        state=state)

        elif(user_role == EnumUserRole.parkinglot):

            return await self.get_parkinglot_abstract_online_reservations(lot_id=user_id,
                                                                        limit=limit,
                                                                        offset=offset,
                                                                        state=state)

        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User type isn't valid !")


    async def get_reservation_details(self,
                                      user_role: EnumUserRole,
                                      user_id:int,
                                      reservation_id:int
                                      ):

        if(user_role == EnumUserRole.customer):
            return await self.get_customer_detailed_reservation(customer_id=user_id,
                                                                reservation_id=reservation_id)

        elif(user_role == EnumUserRole.parkinglot):
            return await self.get_parkinglot_detailed_reservation(lot_id=user_id,
                                                                  reservation_id=reservation_id)

        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User type isn't valid !")


    async def get_customer_abstract_online_reservations(self,
                                               customer_id: int,
                                               limit:Optional[int]=None,
                                               offset:Optional[int]=None,
                                               state: Optional[EnumReservationState] = None):

        reservations = await self.online_reservations_repo.get_customer_reservations(customer_id=customer_id,
                                                                                     limit=limit,
                                                                                     offset=offset,
                                                                                     state=state)

        if(reservations):
            reservations = [OnlineReservationDB.from_orm(reservation) for reservation in reservations]
            return await self._get_customer_abstract_online_reservations_helper(reservations=reservations)

        return []


    async def get_customer_detailed_reservation(self,
                                                customer_id: int,
                                                reservation_id: int):
        reservation = await self.online_reservations_repo.get_reservation_by_id(id=reservation_id)
        if(reservation):
            reservation = OnlineReservationDB.from_orm(reservation)
            if(self._customer_owns_reservation(customer_id = customer_id,
                                               reservation = reservation)):
                return await self._get_customer_detailed_online_reservation_helper(reservation=reservation)
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="You don't own this reservation.")

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No reservation with the provided id was found.")


    async def get_parkinglot_detailed_reservation(self,
                                                  lot_id:int,
                                                  reservation_id: int):

        reservation = await self.online_reservations_repo.get_reservation_by_id(id = reservation_id)
        if(reservation):
            reservation = OnlineReservationDB.from_orm(reservation)

            if(await self._lot_owns_reservation(lot_id = lot_id,
                                          reservation = reservation)):
                return await self._get_lot_detailed_online_reservation_helper(reservation=reservation)
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="You don't own this reservation.")

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No reservation with the provided id was found.")


    async def get_parkinglot_abstract_online_reservations(self,
                                                          lot_id: int,
                                                          limit: Optional[int] = None,
                                                          offset: Optional[int] = None,
                                                          state: Optional[EnumReservationState] = None):

        slots = await self.slots_repo.get_all_parkinglot_slots(lot_id=lot_id)
        if(slots):
            slots = [ParkingSlotDB.from_orm(slot) for slot in slots]
            slots_ids = [slot.id for slot in slots]
        else:
            return []

        reservations = await self.online_reservations_repo.get_reservations_by_slots_ids(slots_ids=slots_ids,
                                                                                         state=state,
                                                                                         limit =limit,
                                                                                         offset=offset)

        if(reservations):
            reservations_list = [OnlineReservationDB.from_orm(r) for r in reservations]

            return await self._get_lot_abstract_online_reservations_helper(reservations=reservations_list)

        else:
            return []


    def _customer_owns_reservation(self,
                                        customer_id:int,
                                        reservation:OnlineReservationDB):
        if(reservation.customer_id == customer_id):
            return True
        return False


    async def _lot_owns_reservation(self,
                                    lot_id: int,
                                    reservation: OnlineReservationDB):
            slot = await self.slots_repo.get_slot_by_id(reservation.slot_id)
            if(slot):
                slot = ParkingSlotDB.from_orm(slot)
                if(slot.lot_id == lot_id):
                    return True
                return False



    async def _get_customer_abstract_online_reservations_helper(self,
                                                         reservations: list[OnlineReservationDB]):
        abstract_reservations = []
        for reservation in reservations:
            slot = await self.slots_repo.get_slot_by_id(id = reservation.slot_id)
            if(slot):
                slot = ParkingSlotDB.from_orm(slot)
                lot = await self.lots_repo.get_lot_by_id(id=slot.lot_id)
                if(lot):
                    lot = ParkingLotDB.from_orm(lot)

                    abstract_reservation = CustomerReservationAbstract(duration=reservation.duration,
                                                                        id=reservation.id,
                                                                        state=reservation.state,
                                                                        lot_name=lot.lot_name)
                    abstract_reservations.append(abstract_reservation)

        return abstract_reservations


    async def _get_customer_detailed_online_reservation_helper(self,
                                         reservation: OnlineReservationDB):

        slot = await self.slots_repo.get_slot_by_id(id = reservation.slot_id)
        if(slot):
            slot = ParkingSlotDB.from_orm(slot)
            lot = await self.lots_repo.get_lot_by_id(id=slot.lot_id)

            if(lot):
                lot = ParkingLotDB.from_orm(lot)
                detailed_reservation = CustomerReservationDetails(id=reservation.id,
                                                                duration=reservation.duration,
                                                                start_time=reservation.start_time,
                                                                state=reservation.state,
                                                                total_pay=reservation.total_pay,
                                                                lot_name=lot.lot_name)

                return detailed_reservation

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The requested resources has data that don't exist anymore.")


    async def _get_lot_detailed_online_reservation_helper(self,
                                         reservation: OnlineReservationDB):
        customer = await self.customers_repo.get_customer_by_id(id = reservation.customer_id)
        if(customer):
            customer = CustomerDB.from_orm(customer)
            return LotReservationDetails(duration=reservation.duration,
                                      id=reservation.id,
                                      start_time=reservation.start_time,
                                      state=reservation.state,
                                      total_pay=reservation.total_pay,
                                      phone_number=customer.phone_number,
                                      customer_name=customer.name,
                                         vehicle_number=customer.vehicle_number)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The requested resources has data that don't exist anymore.")



    async def _get_lot_abstract_online_reservations_helper(self,
                                                reservations: list[OnlineReservationDB]):
        customers_ids = [r.customer_id for r in reservations]
        customers = await self.customers_repo.get_customers_by_ids(ids=customers_ids)
        customers_list = [CustomerDB.from_orm(c) for c in customers]

        abstract_reservations = []

        for reservation in reservations:
            customer = self._customer_from_id(customers=customers_list,
                                              customer_id=reservation.customer_id)
            if(customer):
                abstract_reservation = LotReservationAbstract(id=reservation.id,
                                                        duration=reservation.duration,
                                                        state=reservation.state,
                                                        customer_name=customer.name)

                abstract_reservations.append(abstract_reservation)

        return abstract_reservations


    def _customer_from_id(self,
                          customers: list[CustomerDB],
                          customer_id: int):
        for customer in customers:
            if(customer.id == customer_id):
                return customer

        return None


    async def _update_reservation_state(self,
                                       reservation_id: int,
                                       state: EnumReservationState):

        await self.online_reservations_repo.update_reservation(id = reservation_id,
                                                    details={"state" :state
                                                    })
