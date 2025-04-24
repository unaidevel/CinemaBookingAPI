from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import date
import uuid
from app.models.booking import Booking  
from typing import List





class UserBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
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

    bookings: list["Booking"] = Relationship(back_populates='user')

class UserPublic(UserBase):
    pass