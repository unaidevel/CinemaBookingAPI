from fastapi import APIRouter, Depends, status
from app.models import Booking, UserInDb, Session, BookingPublic, BookingIn, Seat, BookingOut, Booking_with_Seats, release_expired_seats, lock_seats
from typing import Annotated, Dict, List
from app.auths.auth import SessionDep
from app.auths.dependency import admin_only
from app.auths.auth import get_current_user, get_current_active_user
from uuid import UUID
from sqlmodel import select
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import selectinload
from datetime import datetime
# from app.routers import simple_send, EmailSchema
from app.routers.mail_sending import simple_send, EmailSchema


booking_router = APIRouter()


@booking_router.post('/session/{session_id}/booking', response_model=BookingPublic, tags=['Bookings'])
async def create_reserve(
    session_id: UUID,
    booking_in: BookingIn,
    session: SessionDep,
    current_user: Annotated[UserInDb, Depends(get_current_active_user)]
):
    release_expired_seats(session)

    if not booking_in.seat_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='seat_ids cannot be empty')
    
    seats = session.exec(select(Seat).where(Seat.session_id==session_id, Seat.id.in_(booking_in.seat_ids))).all()
    # seats = session.exec(select(Seat).where(Seat.id.in_(booking_in.seat_ids))).all()
    if len(seats) != len(booking_in.seat_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='One or more seats not found')
    if any(seat.is_reserved for seat in seats):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='One or more seats already reserved')
    # if any(seat.session_id != booking_in.session_id for seat in seats):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Some seats do not belong to the session')

    lock_seats(session, booking_in.seat_ids)
    film_session = session.exec(select(Session).where(Session.id==session_id)).first()
    if not film_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')
    
    booking = Booking(**booking_in.model_dump(exclude='seat_ids'))
    booking.status = 'completed'
    booking.movie_id = film_session.movie_id
    booking.user_id = current_user.id
    booking.session_id = session_id
    session.add(booking)
    session.commit()
    session.refresh(booking)

    for seat in seats:
        seat.booking_id = booking.id
        seat.is_reserved = True
    session.add_all(seats)
    session.commit()

    # await simple_send(EmailSchema(email=[current_user.email]))
    return booking


@booking_router.get('/user/bookings', response_model=list[BookingPublic], tags=['Bookings'])
async def get_user_bookings(
    session:SessionDep, 
    current_user: Annotated[UserInDb, Depends(get_current_active_user)]
):
    all_bookings = session.exec(select(Booking).where(Booking.user_id == current_user.id)).all()
    if not all_bookings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Seats not found!')
    bookings = [BookingPublic.model_validate(b) for b in all_bookings]
    return bookings

@booking_router.get('/user/bookings/{booking_id}', response_model=Booking_with_Seats, tags=['Bookings'])
async def read_booking_by_id(
    booking_id: UUID, 
    session:SessionDep, 
    current_user: Annotated[str, Depends(get_current_active_user)]
):
    booking = session.exec(select(Booking)
                                 .where(Booking.id == booking_id)
                                 .options(selectinload(Booking.seats))).first()  #selectinload allows to load relationships
    
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Booking not found!')
    return booking
    

@booking_router.get('/user/booking/history', response_model=list[BookingPublic], tags=['Bookings'])
async def read_user_booking_history(
    session: SessionDep, 
    current_user: Annotated[str, Depends(get_current_active_user)]
):
    present_bookings = session.exec(select(Booking).where(Booking.booking_date >= datetime.now(datetime.UTC))).all()
    past_bookings = session.exec(select(Booking).where(Booking.booking_date <= datetime.now(datetime.UTC))).all()

    return present_bookings + past_bookings

@booking_router.delete('/bookings/cancel_booking/{booking_id}', tags=['Bookings'])
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