from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from app.database import SessionDep
from app.models import UserPublic, UserPassword, UserInDb, UserCreate
from app.auths.utils import TokenRefresh, Token, TokenData
from fastapi.exceptions import HTTPException
from fastapi import status, Depends
from datetime import timedelta, datetime, timezone, UTC
import jwt 
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from sqlmodel import select
from app.config import DATABASE_URL, SECRET_KEY
from uuid import UUID

# settings = get_settings()

SECRET_KEY = SECRET_KEY
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_TIME = 60 * 24 * 7


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hashed(password):
    return pwd_context.hash(password)


def get_user(username: str, session: SessionDep) -> UserInDb | None:
    user = session.exec(select(UserInDb).where(UserInDb.username == username)).first()
    if user:
        return user
        # user_dict = user.__dict__ #As i saw, if i dont have schemas, its essential to convert the pydantic to dict, and remove the password
        # user_dict.pop('hashed_password', None)
        # return user_dict
    return None 



def authenticate_user(username: str, password: str, session:SessionDep):
    user = get_user(username=username, session=session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else: 
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token_in_db(user_id: UUID, username: str, session: SessionDep) -> str:
    refresh_token = create_refresh_token(data={"username": username})

    expires_at = datetime.now(UTC) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_TIME)

    db_token = TokenRefresh(
        token=refresh_token,
        user_id=user_id,
        expires_at=expires_at
    )
    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    return db_token.token


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('username')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
        current_user: Annotated[UserInDb, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user

class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: Annotated[UserInDb, Depends(get_current_active_user)]):
        if user.role in self.allowed_roles:
            return True
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="You don't have enough permissions")
    

def validate_refresh_token(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        result = session.exec(select(TokenRefresh).where(TokenRefresh.token == token)).first()
        return result
    except Exception as e:
        return credentials_exception    
