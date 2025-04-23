from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date


class Movie(SQLModel, table=True):
    id: uuid = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(max_length=500, unique=True)
    genre: str
    showtime: date 