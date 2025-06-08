from fastapi import APIRouter, Depends, status, Body
from sqlmodel import select
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.database import SessionDep
from datetime import timedelta, datetime, timezone, UTC
from app.auths.auth import create_access_token, authenticate_user, get_password_hashed, get_current_user, create_refresh_token_in_db
from app.auths.auth import oauth2_scheme
from app.auths.utils import TokenRefresh, Token, AccessToken, RefreshTokenRequest
from app.auths.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import UserInDb, UserPassword, UserPublic, UserUpdate
from fastapi.exceptions import HTTPException
from app.config import SECRET_KEY
from jose import JWTError, jwt

user_router = APIRouter()

ALGORITHM = 'HS256'

@user_router.post('/token', tags=['User'])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Username or password is not correct', headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token_in_db(user.id, user.username, session)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


    # return Token(access_token=access_token, token_type="bearer")


@user_router.post('/refresh', tags=['User'])
def refresh_access_token(
    token_data: RefreshTokenRequest,
    session: SessionDep
) -> AccessToken:
    refresh_token = token_data.refresh_token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token, JWT Error')
    
    db_token = session.exec(select(TokenRefresh).where(TokenRefresh.token==refresh_token)).first()


    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token!')
    
    expires_at_aware = db_token.expires_at.replace(tzinfo=timezone.utc)

    if expires_at_aware < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token expired!')

    # if db_token.expires_at < datetime.now(timezone.utc):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token expired!')


    new_access_token = create_access_token(data={"username": username})

    return {
        "access_token": new_access_token, 
        "token_type": "bearer"
    }



@user_router.post('/user', response_model=UserPublic, tags=['User'])
async def create_user(
    user: UserPassword, 
    session: SessionDep
):
    create_hashed_password = get_password_hashed(user.password)
    user_in_db = UserInDb(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=create_hashed_password,
        is_active=True,
        birth_date=user.birth_date,
        role='user'
    )
    session.add(user_in_db)
    session.commit()
    session.refresh(user_in_db)
    return user_in_db


@user_router.post('/logout', tags=['User'])
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)], 
    session: SessionDep
):
    result = session.exec(select(TokenRefresh).where(TokenRefresh.token == token)).first()
    if result:
        session.delete(result)
        session.commit()
    
    return {"message": "Logged out succesfully"}



@user_router.get('/user/me', response_model=UserPublic, tags=['User'])
async def read_user_me(
    current_user: Annotated[UserInDb, Depends(get_current_user)]
):
    return current_user


@user_router.patch('/user/me', response_model=UserPublic, tags=['User'])
async def edit_user_data(
    user_update: UserUpdate,
    session: SessionDep,
    current_user: Annotated[UserInDb, Depends(get_current_user)]
):
    user_in_db = session.get(UserInDb, current_user.id)
    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found!')
    
    user_data = user_update.model_dump(exclude_unset=True)
    user_in_db.sqlmodel_update(user_data)
    session.add(user_in_db)
    session.commit()
    return user_in_db
