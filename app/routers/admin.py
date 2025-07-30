from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated
from app.auths.dependency import admin_only
from app.models import UserInDb, Booking, RatingDB, Session, Movie, BookingPublicAdminOnly
from app.database import SessionDep
from uuid import UUID
admin_router = APIRouter()




@admin_router.post('/admin-only/', tags=['Admin'])
async def admin_only_endpoint(
    current_user: Annotated[UserInDb, Depends(admin_only)]
):
    return {"message": "You have admin access"}


@admin_router.get("/admin-only", response_model=[[BookingPublicAdminOnly], []], tags=['Admin'])
async def admin_advanced_info(
    film_id: UUID,
    session: SessionDep, 
    current_user: Annotated[UserInDb, Depends(admin_only)],
    limit: Annotated[int, Query(le=100)] = 100,
    offset: int = 0):

    all_bookings_for_movie = session.exec(Booking).where(Booking.movie_id == film_id)
    if not all_bookings_for_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No bookings for this movie')

    all_sessions_per_movie = session.exec(Session).where(Session.movie_id == film_id)
    if not all_sessions_per_movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No sessions found for this movie')
    
    
    return {'bookings':all_bookings_for_movie, 'sessions': all_sessions_per_movie}



