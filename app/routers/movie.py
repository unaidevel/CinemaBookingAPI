from fastapi import APIRouter, Depends
from typing import Annotated
from app.models import Court, UserInDb
from app.auths.auth import SessionDep
from app.auths.dependency import admin_only

router = APIRouter()

@router.post('/movie', response_model=Court)
async def create_movie(movie:Court, session:SessionDep, current_user: Annotated[UserInDb, Depends(admin_only)]):
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie