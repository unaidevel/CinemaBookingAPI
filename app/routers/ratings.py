from app.models import RatingCreate, RatingDB, RatingPublic, Movie
from fastapi import APIRouter, Depends
from app.auths.auth import SessionDep, get_current_active_user, get_current_user
from typing import Annotated
from sqlmodel import select




rating_router = APIRouter()


@rating_router.post('/movie/review', response_model=RatingPublic)
async def create_review_for_movie(
    rating: RatingCreate,
    session: SessionDep,
    current_user: Annotated[str, Depends(get_current_active_user)]
):
    existing_rating = session.exec(select(Movie).where )
    pass