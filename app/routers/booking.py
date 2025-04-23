from fastapi import APIRouter, Depends
from app.models import Booking, UserInDb
from typing import Annotated
from app.auths.auth import SessionDep, get_current_user

router = APIRouter()


@router.post('/booking/', response_model=Booking)
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