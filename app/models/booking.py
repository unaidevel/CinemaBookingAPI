from sqlmodel import SQLModel, Field, Relationship
import uuid
from app.models.user import UserInDb
from app.models.movie import Movie

class Booking(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    booking_date: date
    user_id: uuid.UUID = Field(foreign_key='userindb.id')
    court_id: uuid.UUID = Field(foreign_key='court.id')

    

    user: UserInDb = Relationship(back_populates='booking')
    movie: Movie = Relationship(back_populates='booking')
