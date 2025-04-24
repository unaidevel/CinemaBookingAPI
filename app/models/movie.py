from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date
from datetime import datetime, timezone
import enum
import alembic_postgresql_enum
from typing import Literal
from .session import Session
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .session import Session


class Movie(SQLModel, table=True):
    id: uuid = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=100, unique=True, index=True)
    description: str = Field(max_length=500, unique=True)
    release_date: date = Field(default_factory=lambda:datetime.now(timezone.utc).date())
    duration: int
    genre: Literal['action', 'thriller', 'drama', 'comedy', 'horror', 'western']
    showtime: date 


    sessions: list["Session"] = Relationship('Session', back_populates='movie')