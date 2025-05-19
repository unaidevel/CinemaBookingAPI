from sqlmodel import SQLModel, Relationship, Field, select
from typing import Optional
import uuid
from app.models import Session, Booking
from datetime import datetime, timedelta, timezone,UTC
from app.auths.auth import SessionDep
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy import UniqueConstraint



class Seat(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("session_id", "seat_number", name="uix_session_seat")), #uix_session_seat is just the name of session_id and seat number both combined being unique
    #This table args forces to not duplicate seats in one session
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    seat_number: str
    session_id: uuid.UUID = Field(foreign_key='session.id')
    locked_until: datetime = Field(nullable=True)

    is_reserved: bool = False

    booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key='booking.id')

    session: Optional['Session'] = Relationship(back_populates='seats')
    booking: Optional['Booking'] = Relationship(back_populates='seats')

    
class SeatOut(SQLModel):
    seat_number: str
    is_reserved: bool



def generate_seats_for_session(session_id: uuid.UUID) -> list[Seat]:
    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    columns = list(range(1, 16))
    seats = []

    for row in rows:
        for col in columns:
            seat_number = f'{row}{col}'
            seats.append(Seat(seat_number=seat_number, session_id=session_id))
    return seats
        


def lock_seats(session: SessionDep, seat_ids: list[uuid.UUID]):
    seats = session.exec(select(Seat).where(Seat.id.in_(seat_ids))).all()
    now = datetime.now(timezone.utc)

    if not seats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Seat not found')

    for seat in seats:
        if seat.is_reserved:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Seat already booked')

        if seat.locked_until and seat.locked_until.tzinfo is None:
            seat.locked_until = seat.locked_until.replace(tzinfo=timezone.utc)
        if seat.locked_until and seat.locked_until > now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Seat is currently locked')

        seat.locked_until = now + timedelta(minutes=5)

    session.add_all(seats)
    session.commit()
    return {
        "locked_seats": [str(seat.seat_number) for seat in seats],
        "locked_until": seats[0].locked_until.isoformat() if seats else None
    }



def release_expired_seats(session: SessionDep):
    now = datetime.now(timezone.utc)
    statement = select(Seat).where(Seat.locked_until != None, Seat.locked_until < now)
    expired = session.exec(statement).all()
    for seat in expired:
        seat.locked_until = None
    session.commit()