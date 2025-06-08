import pytest
from uuid import uuid4
from app.models import Session, Seat



def test_get_seats_returns_valid_structure(client, db_session, test_session, test_seats):
    response = client.get(f"/session/{test_session.id}/seats")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    
    for row, seats in data.items():
        assert isinstance(row, str)
        assert isinstance(seats, list)
        for seat in seats:
            assert 'id' in seat
            assert 'seat_number' in seat
            assert 'is_reserved' in seat




def test_seats_are_sorted_by_number(client, test_session, test_seats):
    response = client.get(f"/session/{test_session.id}/seats")
    data = response.json()

    for row, seats in data.items():
        numbers = [int(seat["seat_number"][1:]) for seat in seats]
        assert numbers == sorted(numbers), f"Asientos mal ordenados en fila {row}"


def test_reserved_seat_marked_correctly(client, db_session, test_session, test_seats):
    # Simula reservar un asiento
    seat = test_seats[0]
    seat.is_reserved = True
    db_session.add(seat)
    db_session.commit()

    response = client.get(f"/session/{test_session.id}/seats")
    data = response.json()

    row = seat.seat_number[0]
    found = next(s for s in data[row] if s["id"] == str(seat.id))
    assert found["is_reserved"] is True


@pytest.fixture
def test_session(db_session):
    session = Session(id=uuid4(), session_time="2025-06-01T18:00", movie_id=uuid4(), price=8.0)
    db_session.add(session)
    db_session.commit()
    return session

@pytest.fixture
def test_seats(db_session, test_session):
    seats = [
        Seat(seat_number=f"A{i+1}", session_id=test_session.id)
        for i in range(5)
    ]
    db_session.add_all(seats)
    db_session.commit()
    return seats