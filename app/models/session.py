from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional
from datetime import datetime



if TYPE_CHECKING:
    from .movie import Movie
    from .booking import Booking
    from .user import UserInDb
    from .seats import Seat


class SessionBase(SQLModel):
    session_time: datetime
    room: str
    price: float

class SessionIn(SessionBase):
    movie_id: uuid.UUID

class SessionPublic(SessionBase):
    id: uuid.UUID
    

class SessionUpdate(SQLModel):
    
    session_time: datetime | None = None    
    room: str | None = None
    price: float | None = None

class Session(SessionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    movie_id: uuid.UUID = Field(foreign_key='movie.id')
    # session_time: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())

    movie: 'Movie' = Relationship(back_populates='sessions')
    bookings: list['Booking'] = Relationship(back_populates='session')
    seats: list['Seat'] = Relationship(back_populates='session')


# class Session(SQLModel, table=True):
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     movie_id: uuid.UUID = Field(foreign_key='movie.id')
#     session_time: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
#     room: str
#     price: float


#     movie: Optional['Movie'] = Relationship(back_populates='sessions')
#     bookings: list['Session'] = Relationship(back_populates='session')



    