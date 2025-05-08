from fastapi import APIRouter, Depends, status
from app.models import Booking, UserInDb, BookingPublic, BookingIn, Seat, Booking_with_Seats
from typing import Annotated, Dict, List
from app.auths.auth import SessionDep
from app.auths.dependency import admin_only
from app.auths.auth import get_current_user
from uuid import UUID
from sqlmodel import select
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import selectinload
from datetime import datetime

booking_router = APIRouter()


@booking_router.post('/session/{session_id}/booking', response_model=BookingPublic)
async def create_reserve(
    booking_in: BookingIn,
    session: SessionDep,
    current_user: Annotated[UserInDb, Depends(get_current_user)]
):
    
    seats = session.exec(select(Seat).where(Seat.id.in_(booking_in.seat_ids))).all()
    if len(seats) != len(booking_in.seat_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='One or more seats not found')
    if any(seat.is_reserved for seat in seats):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='One or more seats already reserved')
    
    if any(seat.session_id != booking_in.session_id for seat in seats):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Some seats do not belong to the session')

    booking = Booking(**booking_in.model_dump(exclude='seat_ids'))
    booking.status = 'completed'
    booking.user_id = current_user.id
    session.add(booking)
    session.commit()
    session.refresh(booking)

    for seat in seats:
        seat.booking_id = booking.id
        seat.is_reserved = True
    session.add_all(seats)
    session.commit()
    return booking


@booking_router.get('/user/bookings', response_model=Booking_with_Seats)
async def get_user_bookings(
    session:SessionDep, 
    current_user: Annotated[str, Depends(get_current_user)]
):
    all_bookings = session.exec(select(Booking).where(Booking.user_id == current_user.id)).all()
    if not all_bookings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Seats not found!')
    
    return all_bookings

@booking_router.get('/user/bookings/{booking_id}', response_model=Booking_with_Seats)
async def read_booking_by_id(
    booking_id: UUID, 
    session:SessionDep, 
    current_user: Annotated[str, Depends(get_current_user)]
):
    booking = session.exec(select(Booking)
                                 .where(Booking.id == booking_id)
                                 .options(selectinload(Booking.seats))).first()  #selectinload allows to load relationships
    
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Booking not found!')
    return booking
    

@booking_router.get('/user/booking/history', response_model=list[BookingPublic])
async def read_user_booking_history(
    session: SessionDep, 
    current_user: Annotated[str, Depends(get_current_user)]
):
    present_bookings = session.exec(select(Booking).where(Booking.booking_date >= datetime.now(datetime.UTC))).all()
    past_bookings = session.exec(select(Booking).where(Booking.booking_date <= datetime.now(datetime.UTC))).all()

    return present_bookings + past_bookings

@booking_router.delete('/booking/cancel_booking/{booking_id}')
async def delete_booking(
    booking_id:UUID, 
    session: SessionDep, 
    current_user: Annotated[str, Depends(admin_only)]
):
    reserve = session.get(Booking, booking_id)
    if not reserve:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail='Reserve not found')
    session.delete(reserve)
    session.commit()
    return {"message": "Booking deleted succesfully!"}


