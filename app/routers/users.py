from fastapi import APIRouter, Depends, status
from sqlmodel import select
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.database import SessionDep
from datetime import timedelta
from app.auths.auth import create_access_token, authenticate_user, get_password_hashed, get_current_user
from app.auths.auth import oauth2_scheme, TokenRefresh, Token
from app.auths.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import UserInDb, UserPassword, UserPublic
from fastapi.exceptions import HTTPException



user_router = APIRouter()



@user_router.post('/token')
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(SessionDep, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='User not found', headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")





@user_router.post('/user/', response_model=UserPublic)
async def create_user(user: UserPassword, session: SessionDep):
    hashed_password = get_password_hashed(user.password)
    user_in_db = UserInDb(
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        role='user'
    )
    session.add(user_in_db)
    session.commit()
    session.refresh(user_in_db)
    return user_in_db


@user_router.post('/logout/')
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    result = session.exec(select(TokenRefresh).where(TokenRefresh.token == token)).first()
    if result:
        session.delete(result)
        session.commit()
    
    return {"message": "Logged out succesfully"}



@user_router.post('/user/me/', response_model=UserPublic)
async def read_user_me(
    current_user: Annotated[UserInDb, Depends(get_current_user)]
):
    return current_user
