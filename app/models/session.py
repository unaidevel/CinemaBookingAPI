from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .movie import Movie



class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    movie_id: uuid.UUID = Field(foreign_key='movie.id')
    session_time: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())

    movie: Optional['Movie'] = Relationship(back_populates='session')
    
