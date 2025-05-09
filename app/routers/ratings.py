from app.models import RatingCreate, RatingDB, RatingPublic, Movie
from fastapi import APIRouter, Depends, Query, status
from app.auths.auth import SessionDep, get_current_active_user, get_current_user
from typing import Annotated
from sqlmodel import select
from uuid import UUID
from fastapi.exceptions import HTTPException



rating_router = APIRouter()


@rating_router.post('/{movie_id}/review', response_model=RatingPublic)
async def create_review_for_movie(
    movie_id: str,
    ratingIn: RatingCreate,
    session: SessionDep,
    current_user: Annotated[str, Depends(get_current_active_user)]
):

    existing_rating = session.exec(select(RatingDB).where(RatingDB.user_id == current_user.id, RatingDB.movie_id== movie_id)).first()
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You've already written a review about this film!")

    rating = RatingDB(**ratingIn.model_dump())
    rating.user_id = current_user.id
    rating.movie_id = movie_id

    session.add(rating)
    session.commit()
    session.refresh(rating)
    return rating



#return all reviews of a movie
@rating_router.get('/movie/review', response_model=RatingPublic)
async def read_all_reviews_of_a_movie(
    movie_id: UUID,
    session: SessionDep,
    limit: Annotated[int, Query(le=100)] = 100,
    offset: int = 0
):
    query = select(RatingDB).where(RatingDB.movie_id==movie_id)
    final_query = query.offset(offset).limit(limit)
    all_reviews = session.exec(final_query).all()
    if not all_reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not reviews for this movie!')
    return all_reviews


#Search review of a movie by id
@rating_router.get('/movie/rating/{rating_id}', response_model=RatingPublic)
async def read_single_review(
    rating_id: UUID,
    session: SessionDep,
):
    review = session.exec(select(RatingDB)).where(RatingDB.id == rating_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found!')
    return review
