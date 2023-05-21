from datetime import datetime,timedelta
from typing import Optional,Union
from fastapi import Depends, HTTPException,status
from sqlalchemy import select
from models.reservations import OnlineReservation
from core.security import verify_password, hash_password
from core.jwt import create_access_token, decode_access_token
from schemas.parking_slots import *
from schemas.parking_lot import *
from schemas.reservation import *
from schemas.jwt import *
from repositories.reservations import OnlineReservationsRepository
from repositories.parking_slots import ParkingSlotsRepository
from repositories.parking_lots import ParkinglotsRepository,EnumOrder,EnumOrderBy


class ParkingLotsService:
    def __init__(self,
                 online_reservations_repo:OnlineReservationsRepository = Depends(OnlineReservationsRepository),
                 slots_repo:ParkingSlotsRepository = Depends(ParkingSlotsRepository),
                 lots_repo:ParkinglotsRepository = Depends(ParkinglotsRepository),
                ) -> None :

        self.online_reservations_repo = online_reservations_repo
        self.slots_repo = slots_repo
        self.lots_repo = lots_repo


    async def login(self,
                    lot_name:str,
                    secret:str):

        lot = await self._authenticate(lot_name=lot_name,
                                      secret=secret)
        if(lot):
            return {
                "access_token" : create_access_token(role=EnumUserRole.parkinglot,
                                                     subject = lot.id),
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect lot secret.")


    async def get_lot_from_token(self,
                                 token:str):
        try:
            token_data = decode_access_token(token=token)
            token_data = JWTSchema(**token_data)

            if(token_data.role == EnumUserRole.parkinglot):
                if(token_data.expiration_date<datetime.now()):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token Expired. please login again.")

                lot = await self.lots_repo.get_lot_by_id(id=token_data.id)
                lot = ParkingLotDB.from_orm(lot)
                return lot

            else:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="This action is not allowed for this type of user.")

        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not valid."
                )


    async def _authenticate(self,
                           lot_name:str,
                           secret:str):

        lot = await self.lots_repo.get_lot_by_name(name = lot_name)
        if(lot):
            lot = ParkingLotDB.from_orm(lot)
            if(verify_password(lot.lot_secret,secret)):
                return lot

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There's no parking lot with the provided lot name.")


    async def add_parkinglot(self,
                             parking_lot: CreateParkingLot):

        lot_with_same_name = await self.lots_repo.get_lot_by_name(name=parking_lot.lot_name)
        if(lot_with_same_name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="A lot with the same name already exists!")


        parking_lot = ParkingLotDB(lot_name=parking_lot.lot_name,
                                   address=parking_lot.address,
                                   lot_secret=hash_password(password=str(parking_lot.lot_secret)),
                                   hourly_pay=parking_lot.hourly_pay,
                                   allowance_time=parking_lot.allowance_time,
                                   capacity=parking_lot.capacity,
                                   longitude=parking_lot.longitude,
                                   lattitude=parking_lot.lattitude,
                                   description=parking_lot.description,
                                   picture= parking_lot.picture)


        await self.lots_repo.add_lot(parking_lot=parking_lot)
        await self._create_parkinglot_slots(lot_name=parking_lot.lot_name)



    async def _create_parkinglot_slots(self,
                               lot_name: str):

        parking_lot = await self.lots_repo.get_lot_by_name(name=lot_name)
        if(parking_lot):

            for i in range(1,parking_lot.capacity+1):
                slot = CreateParkingSlot(lot_id=parking_lot.id,
                                        slot_number=i,
                                        is_occupied=False)
                await self.slots_repo.add_slot(slot=slot)


    async def get_abstract_parkinglots_data(self,
                              limit: Optional[int] = None,
                              offset: Optional[int] = None,
                              order_by:Optional[EnumOrderBy] = None,
                              order: Optional[EnumOrder] = None,
                              ):

        lots = await self.lots_repo.get_lots(limit=limit,
                                             offset=offset,
                                             order_by=order_by,
                                             order=order)

        if(lots):
            data = []
            lots = [ParkingLotDB.from_orm(lot) for lot in lots]
            for lot in lots:
                lot_data = await self._get_abstract_parkinglot_data_helper(parking_lot=lot)
                data.append(lot_data)

            return data


    async def get_abstract_parkinglot_data(self,
                                           lot_id: int):
        parking_lot = await self.lots_repo.get_lot_by_id(id = lot_id)

        if(parking_lot):
            parking_lot = ParkingLotDB.from_orm(parking_lot)
            return await self._get_abstract_parkinglot_data_helper(parking_lot=parking_lot)

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Parking lot was not found.")


    async def get_detailed_parkinglot_data(self,
                           lot_id: int):
        parking_lot = await self.lots_repo.get_lot_by_id(id = lot_id)

        if(parking_lot):
            parking_lot = ParkingLotDB.from_orm(parking_lot)
            return await self._get_detailed_parkinglot_data_helper(parking_lot=parking_lot)

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Parking lot was not found.")


    async def _get_detailed_parkinglot_data_helper(self,
                     parking_lot: ParkingLotDB):

        free_slots = await self.slots_repo.get_parkinglot_free_slots(lot_id=parking_lot.id)
        free_slots = [ParkingSlotDB.from_orm(slot) for slot in free_slots]
        free_slots_numbers = [free_slot.slot_number for free_slot in free_slots]

        return {"id":parking_lot.id,
                "lot_name":parking_lot.lot_name,
                "address": parking_lot.address,
                "description": parking_lot.description,
                "hourly_pay": parking_lot.hourly_pay,
                "allowance_time": parking_lot.allowance_time,
                "available_spaces":free_slots_numbers,
                "num_available_spaces": len(free_slots),
                "max_duration":12}


    async def _get_abstract_parkinglot_data_helper(self,
                     parking_lot: ParkingLotDB):

        free_slots = await self.slots_repo.get_parkinglot_free_slots(lot_id=parking_lot.id)
        if(free_slots):
            free_slots = [ParkingSlotDB.from_orm(slot) for slot in free_slots]
        else:
            free_slots = []


        return {"id":parking_lot.id,
                "lot_name":parking_lot.lot_name,
                "address": parking_lot.address,
                "hourly_pay": parking_lot.hourly_pay,
                "allowance_time": parking_lot.allowance_time,
                "num_available_spaces": len(free_slots),
                "max_duration":12}


    async def remove_parkinglot(self,
                                lot_id:int):
        parking_lot = await self.lots_repo.get_lot_by_id(id=lot_id)
        if(parking_lot):
            slots = await self.slots_repo.get_all_parkinglot_slots(lot_id=lot_id)
            for slot in slots:
                await self.slots_repo.delete_slot(id=slot.id)
            await self.lots_repo.delete_lot(id=lot_id)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Parking lot wasn't found.")
