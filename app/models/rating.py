from sqlmodel import SQLModel, Field, Relationship
import uuid
from typing import TYPE_CHECKING
from enum import Enum


if TYPE_CHECKING:
    from .user import UserInDb
    from .movie import Movie



class Stars(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class RatingBase(SQLModel):

    title: str = Field(max_length=50)
    stars: Stars
    review: str = Field(max_length=500)


class RatingCreate(RatingBase):
    pass

class RatingDB(RatingBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    movie_id: uuid = Field(foreign_key='movie.id')
    user_id: uuid = Field(foreign_key='user.id')

    user: 'UserInDb' = Relationship(back_populates='ratings')
    movie: 'Movie' = Relationship(back_populates='ratings')


class RatingPublic(RatingBase):
    id: uuid.UUID


class RatingUpdate(RatingBase):
    
    title: str | None = None
    stars: Stars | None = None
    review: str | None = None