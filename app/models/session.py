from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .movie import Movie



class Session(SQLModel, table=True):
    id: uuid = Field(default_factory=uuid.uuid4, primary_key=True)
    movie_id: uuid = Field(foreign_key='movie.id')
    session_time: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())

    movie: 'Movie' = Relationship('Movie', back_populates='session')
    
