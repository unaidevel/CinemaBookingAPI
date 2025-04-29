from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional
from datetime import datetime



if TYPE_CHECKING:
    from .movie import Movie



class SessionBase(SQLModel):
    session_time: datetime
    room: str
    price: float

class SessionIn(SessionBase):
    movie_id: uuid.UUID

class SessionPublic(SessionBase):
    id: uuid.UUID


class SessionDB(SessionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    movie_id: uuid.UUID = Field(foreign_key='movie.id')
    # session_time: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    movie: Optional['Movie'] = Relationship(back_populates='sessions')

class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    movie_id: uuid.UUID = Field(foreign_key='movie.id')
    session_time: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    room: str
    price: float
    movie: Optional['Movie'] = Relationship(back_populates='sessions')


    
