from fastapi import APIRouter, Depends
from app.models import Booking, UserInDb, BookingPublic
from typing import Annotated
from app.auths.auth import SessionDep
from app.auths.dependency import admin_only
from app.auths.auth import get_current_user
from uuid import UUID


booking_router = APIRouter()


@booking_router.post('/booking', response_model=BookingPublic)
async def create_reserve(
    booking: Booking,
    session: SessionDep,
    current_user: Annotated[UserInDb, Depends(get_current_user)]
):
    booking.user_id = current_user.id
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking

@booking_router.delete('/booking/cancel_booking/{booking_id}')
async def delete_booking(booking_id:UUID, session: SessionDep, current_user: Annotated[str, Depends(admin_only)]):
    reserve = session.get(Booking, booking_id)
    session.delete(reserve)
    session.commit()
    return {"message": "Booking deleted succesfully!"}

