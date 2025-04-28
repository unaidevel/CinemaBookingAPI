from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date
from datetime import datetime, timezone
from typing import Literal
from .session import Session
from typing import TYPE_CHECKING
from enum import Enum


if TYPE_CHECKING:
    from .session import Session



class GenreEnum(str, Enum):
    ACTION = "action"
    THRILLER = "thriller"
    DRAMA = "drama"
    COMEDY = "comedy"
    HORROR = "horror"
    WESTERN = "western"


class Movie(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=100, unique=True, index=True)
    description: str = Field(max_length=500, unique=True)
    release_date: date = Field(default_factory=lambda:datetime.now(timezone.utc).date())
    duration: int
    genre: GenreEnum
    showtime: date 


    sessions: list["Session"] = Relationship(back_populates='movie')


class MovieUpdate(Movie):

    title: str | None = None
    description: str | None = None
    release_date: date | None = None
    duration: int | None = None
    genre: GenreEnum | None = None
    showtime: date | None = None