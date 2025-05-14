from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import date
import uuid

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .booking import Booking
    from .rating import RatingDB
    from auths.utils import TokenRefresh



class UserBase(SQLModel):

    username: str = Field(max_length=15, nullable=False)
    full_name: str = Field(max_length=20, nullable=False)
    email: EmailStr = Field(unique=True, nullable=False)
    birth_date: date

    # booking: List['Booking'] = Relationship(back_populates='user')


class UserCreate(UserBase):
    pass

class UserPassword(UserBase):
    password: str

class UserInDb(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    disabled: bool | None = None
    is_active: bool
    role: str = Field(default='user')

    bookings: list['Booking'] = Relationship(back_populates='user')
    ratings: list['RatingDB'] = Relationship(back_populates='user')
    refresh_tokens: list['TokenRefresh'] = Relationship(back_populates='user')

class UserPublic(UserBase):
    pass


class UserUpdate(SQLModel):
    full_name: str | None = None
    birth_date: date | None = None
    email: EmailStr | None = None