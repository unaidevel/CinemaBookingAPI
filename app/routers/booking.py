from fastapi import APIRouter, Depends
from app.models import Booking, UserInDb
from typing import Annotated
from app.auths.auth import SessionDep
from app.auths.dependency import admin_only

booking_router = APIRouter()


@booking_router.post('/booking', response_model=Booking)
async def create_reserve(
    booking: Booking,
    session: SessionDep,
    current_user: Annotated[UserInDb, Depends(admin_only)]
):
    booking.user_id = current_user.id
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking