from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from app.models import Movie, UserInDb
from app.auths.auth import SessionDep, get_current_user
from app.auths.dependency import admin_only
from sqlmodel import select
from fastapi.exceptions import HTTPException

router = APIRouter()

@router.post('/movie', response_model=Movie)
async def create_movie(movie:Movie, session:SessionDep, current_user: Annotated[UserInDb, Depends(admin_only)]):
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


@router.get('/movie', response_model=Movie)
async def read_movie(session: SessionDep, offset:int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[Movie]:
    movies = session.exec(select(Movie).offset(offset).limit(limit)).all()
    if not movies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found!')
    return movies



@router.get('/movie/{movie_id}', response_model=Movie)
async def read_movie_by_id(movie_title: str, session: SessionDep):
    # movie = session.exec(select(Movie).where(Movie.title==movie_title))
    movie = session.get(Movie, movie_title)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found!')
    return movie


@router.put('/movie/{movie_id}', response_model=Movie)
async def edit_movie(session: SessionDep, movie_title: str, current_user: Annotated[str, Depends(admin_only)]):
    # movie = session.exec(select(Movie).where(Movie.title== movie_title))
    movie = session.get(Movie, movie_title)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found!')
    
    movie_data = Movie.model_dump(exclude_unset=True)
    movie.sqlmodel_update(movie_data)
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie





@router.delete('/movie/{movie_id}')
async def delete_movie(movie_title: str, session: SessionDep):
    # movie = session.exec(select(Movie).where(Movie.title==movie_title))
    movie = session.get(Movie, movie_title)
    session.delete(movie)
    session.commit()
    return {"Movie deleted!": True}