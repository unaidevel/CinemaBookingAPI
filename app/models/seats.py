from sqlmodel import SQLModel, Relationship, Field
from typing import Optional
import uuid
from app.models import Session, Booking


class Seat(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    seat_number: str
    session_id: uuid.UUID = Field(foreign_key='session.id')

    is_reserved: bool = False

    booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key='booking.id')

    session: Optional['Session'] = Relationship(back_populates='seats')
    booking: Optional['Booking'] = Relationship(back_populates='seats')

    
def generate_seats_for_session(session_id: uuid.UUID) -> list[Seat]:
    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    columns = list(range(1, 16))
    seats = []

    for row in rows:
        for col in columns:
            seat_number = f'{row}{col}'
            seats.append(Seat(seat_number=seat_number, session_id=session_id))
    return seats
        