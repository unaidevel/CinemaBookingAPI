from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from app.models import Session, SessionPublic, SessionUpdate
from app.auths.auth import SessionDep
from app.auths.dependency import admin_only
from sqlmodel import select
from fastapi.exceptions import HTTPException
from uuid import UUID

session_router = APIRouter()



@session_router.post('/sessions', response_model=SessionPublic)
async def create_session(new_session: Session,
                         session: SessionDep, 
                         current_user: Annotated[str, Depends(admin_only)]):
    session_existing = session.exec(select(Session).where)
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    return new_session

@session_router.get('/sessions', response_model=SessionPublic)
async def read_sessions(session: SessionDep, offset:int = 0, limit: Annotated[int, Query(le=100)]= 100) -> list[Session]:
    all_sessions = session.exec(select(Session).offset(offset).limit(limit)).all()
    if not all_sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not sessions ongoing!')
    return all_sessions

@session_router.get('/sessions/{session_id}}', response_model=SessionPublic)
async def read_session_by_id(session_id: str, session: SessionDep):
    film = session.get(Session, session_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found')
    return film

@session_router.patch('/sessions/{session_id}', response_model=SessionPublic)
async def update_session_by_id(session_id:str, session_update: SessionUpdate, session: SessionDep, current_user: Annotated[str, Depends(admin_only)]):
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
async def delete_session(session_id: str, session: SessionDep, current_user: Annotated[str, Depends(admin_only)]):
    specific_session = session.get(Session, session_id)
    session.delete(specific_session)
    session.commit()
    return {"message": "Session deleted succesfully!"}