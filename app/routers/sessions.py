from fastapi import APIRouter, Depends, Query, status
from typing import Dict, List
from typing import Annotated
from app.models import Session, SessionPublic, SessionUpdate, Seat, SessionIn
from app.auths.auth import SessionDep, get_current_user, get_current_active_user
from app.auths.dependency import admin_only
from sqlmodel import select
from fastapi.exceptions import HTTPException
from uuid import UUID
from app.models.seats import generate_seats_for_session, release_expired_seats
from collections import defaultdict


session_router = APIRouter()



@session_router.post('/sessions', response_model=SessionPublic)
async def create_session(
    new_session: SessionIn,
    session: SessionDep, 
    current_user: Annotated[str, Depends(admin_only)]
):
    session_existing = session.exec(select(Session).where(Session.id == new_session.id)).first()
    if session_existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Session already exists!')
    
    new_session = Session(**new_session.model_dump())
    session.add(new_session)   #Create session before the seats, needed to have session_id to asign it afterwards
    session.commit()
    session.refresh(new_session)

    seats = generate_seats_for_session(new_session.id)
    session.add_all(seats)
    session.commit()
    return new_session

@session_router.get('/sessions', response_model=list[SessionPublic])
async def read_sessions(
    session: SessionDep, 
    offset:int = 0, 
    limit: Annotated[int, Query(le=100)]= 100
) -> list[Session]:
    all_sessions = session.exec(select(Session).offset(offset).limit(limit)).all()
    if not all_sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not sessions ongoing!')
    return all_sessions

@session_router.get('/sessions/{session_id}', response_model=SessionPublic)
async def read_session_by_id(
    session_id: UUID, 
    session: SessionDep
):
    film = session.get(Session, session_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found')
    return film

@session_router.get('/session/{session_id}/seats', response_model=Dict[str, List[Dict[str, bool]]]) #The output, A dict with dicts of every row, bool for if its reserved or not
async def get_available_seats_per_season(
    session_id: UUID, 
    session: SessionDep, 
    current_user:Annotated[str, Depends(get_current_active_user)]
):  
    
    release_expired_seats(session)
    seats = session.exec(select(Seat).where(Seat.session_id==session_id)).all()
    seats_per_row = defaultdict(list)
    for seat in seats:
        row = seat.seat_number[0]
        number = int(seat.seat_number[1:])
        seats_per_row[row].append({
            "number": number,
            "reserved": seat.is_reserved
        })

    for row in seats_per_row:   #Ordering the seats per row
        seats_per_row[row].sort(key=lambda s: s['number'])  #s is only variable name
    return seats_per_row




@session_router.patch('/sessions/{session_id}', response_model=SessionPublic)
async def update_session_by_id(
    session_id:UUID, 
    session_update: SessionUpdate, 
    session: SessionDep, 
    current_user: Annotated[str, Depends(admin_only)]
):
    specific_session = session.get(Session, session_id)
    if not specific_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found!')
    
    session_data = session_update.model_dump(exclude_unset=True)
    specific_session.sqlmodel_update(session_data)
    session.add(specific_session)
    session.commit()
    session.refresh(specific_session)
    return specific_session


@session_router.delete('/sessions/{session_id}')
async def delete_session(
    session_id: UUID, 
    session: SessionDep, 
    current_user: Annotated[str, Depends(admin_only)]
):
    specific_session = session.get(Session, session_id)
    session.delete(specific_session)
    session.commit()
    return {"message": "Session deleted succesfully!"}