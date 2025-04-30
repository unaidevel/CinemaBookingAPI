from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date, datetime, timezone

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserInDb
    from .movie import Movie
    from .session import Session

# class Booking(SQLModel, table=True):
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     booking_date: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
#     movie_id: uuid.UUID = Field(foreign_key='movie.id')
#     session_id: uuid.UUID = Field(foreign_key='session.id')
#     user_id: uuid.UUID = Field(foreign_key='userindb.id')
    
#     sessions: 'Session' = Relationship(back_populates='booking')
#     user: 'UserInDb' = Relationship(back_populates='booking')
#     movie: 'Movie' = Relationship(back_populates='booking')




class BookingBase(SQLModel):
    booking_date: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    movie_id: uuid.UUID 
    session_id: uuid.UUID 
    user_id: uuid.UUID 

class BookingUpdate(SQLModel): #This model is for an admin endpoint. To be able to change users bookings
    booking_date: date | None = None
    movie_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None



class BookingIn(BookingBase):
    pass


class BookingPublic(BookingBase):
    id: uuid.UUID
    

class Booking(BookingBase, table=True, ):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    movie_id: uuid.UUID = Field(foreign_key='movie.id')
    session_id: uuid.UUID = Field(foreign_key='session.id')
    user_id: uuid.UUID = Field(foreign_key='userindb.id')

    is_canceled: bool = Field(default=False)

    movie: 'Movie' = Relationship(back_populates='bookings')
    session: 'Session' = Relationship(back_populates='bookings')
    user: 'UserInDb' = Relationship(back_populates='bookings')

    def cancel(self):   #Function to cancel a booking for booking_update endpoint for admins 
        self.is_canceled = True