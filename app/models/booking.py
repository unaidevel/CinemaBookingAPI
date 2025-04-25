from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date, datetime, timezone

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserInDb
    from .movie import Movie
    from .session import Session

class Booking(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    booking_date: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    movie_id: uuid.UUID = Field(foreign_key='movie.id')
    session_id: uuid.UUID = Field(foreign_key='session.id')
    user_id: uuid.UUID = Field(foreign_key='userindb.id')
    
    sessions: 'Session' = Relationship(back_populates='booking')
    user: 'UserInDb' = Relationship(back_populates='booking')
    movie: 'Movie' = Relationship(back_populates='booking')
