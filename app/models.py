from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from pydantic import EmailStr, PastDate, BaseModel
import uuid
from typing import List
from enum import Enum
from datetime import datetime



class UserBase(SQLModel):
    id: uuid.UUID = Field(default=uuid.uuid4, primary_key=True)
    username: str = Field(max_length=15)
    full_name: str = Field(max_length=20)
    email: EmailStr = Field(unique=True)
    role: str = Field(default='user')
    disabled: bool | None = None
    birth_date: date
    is_active: bool

    # booking: List['Booking'] = Relationship(back_populates='user')


class UserPassword(UserBase):
    password: str

class UserInDb(UserBase, table=True):
    hashed_password: str

    booking: list['Booking'] = Relationship(back_populates='user')

class UserPublic(UserBase):
    pass

class CourtChoices(str, Enum):
    tennis = 'Tennis court'
    padel = 'Padel court'

class Court(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    court_type: CourtChoices

    booking: List['Booking'] = Relationship(back_populates='court')


class Booking(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    booking_date: date
    user_id: uuid.UUID = Field(foreign_key='userindb.id')
    court_id: uuid.UUID = Field(foreign_key='court.id')

    

    user: UserInDb = Relationship(back_populates='booking')
    court: Court = Relationship(back_populates='booking')


class TokenRefresh(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: uuid.UUID = Field(foreign_key='userindb.id')
    date_created: datetime = Field(default=datetime.now())
    