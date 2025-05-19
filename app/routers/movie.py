from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from app.models import Movie, UserInDb, MovieCreate, MovieUpdate
from app.auths.auth import SessionDep, get_current_user
from app.auths.dependency import admin_only
from sqlmodel import select
from fastapi.exceptions import HTTPException
from slugify import slugify

movie_router = APIRouter()

@movie_router.post('/movie', response_model=Movie, tags=['Movie'])
async def create_movie(
    movieIn:MovieCreate, 
    session:SessionDep, 
    current_user: Annotated[UserInDb, Depends(admin_only)]
):
    # slug = slugify(MovieCreate.title) I removed it because i created the function in Movie model

    existing_movie = session.exec(select(Movie).where(Movie.title == movieIn.title)).first()
    if existing_movie:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Film already exists!')
    
    new_movie = Movie(**movieIn.model_dump())
    new_movie.generate_slug()
    session.add(new_movie)
    session.commit()
    session.refresh(new_movie)
    return new_movie


@movie_router.get('/movie', response_model=list[Movie], tags=['Movie'])
async def read_movie(
    session: SessionDep, 
    title: str | None = None, 
    genre:str | None = None, 
    offset:int = 0, 
    limit: Annotated[int, Query(le=100)] = 100
) -> list[Movie]:
    
    # movies = session.exec(select(Movie).offset(offset).limit(limit)).all()
    # return movies
    query = select(Movie)
    if title:
        query = query.where(Movie.title.ilike(f"%{title}%")) #ilike insensitive like. It works with pattern % %
        #with f'{title}' the return would be exactly the words Example: 'mat' wouldnt match with anything. With %% mat can match with words that contain 'mat'
    if genre:
        query = query.where(Movie.genre.ilike(f"%{genre}%"))

    query = query.offset(offset).limit(limit)
    results = session.exec(query).all()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found!')
    return results


@movie_router.get('/movie/{slug}', response_model=Movie, tags=['Movie'])
async def read_movie_by_id(slug: str, session: SessionDep):
    # movie = session.exec(select(Movie).where(Movie.title==movie_title))
    # movie = session.get(Movie, movie_title)
    movie = session.exec(select(Movie).where(Movie.slug == slug)).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found!')
    return movie


@movie_router.patch('/movie/{slug}', response_model=Movie, tags=['Movie'])
async def edit_movie(session: SessionDep, slug: str, movie_update: MovieUpdate, current_user: Annotated[str, Depends(admin_only)]):
    movie = session.exec(select(Movie).where(Movie.slug== slug)).first()
    # movie = session.get(Movie, movie_title)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found!')
    
    movie_data = movie_update.model_dump(exclude_unset=True) #Exclude unset exclude None fields.
    movie.sqlmodel_update(movie_data)

    # for key, value in movie_data.items():  #Its on the model now.
    #     setattr(movie, key, value)
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie



@movie_router.delete('/movie/{slug}', tags=['Movie'])
async def delete_movie(slug: str, session: SessionDep, current_user: Annotated[str, Depends(admin_only)]):
    movie = session.exec(select(Movie).where(Movie.slug==slug)).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found!')
    session.delete(movie)
    session.commit()
    return {"message": "Movie deleted successfully!"}
