from fastapi import APIRouter, Depends
from typing import Annotated
from app.models import Session
from app.auths.auth import SessionDep
from app.auths.dependency import admin_only
from sqlmodel import select



session_router = APIRouter()


@session_router.post('/sessions', response_model=Session)
async def create_session(new_session: Session,
                         session: SessionDep, 
                         current_user: Annotated[str, Depends(admin_only)]):
    session_existing = session.exec(select(Session).where)
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    return new_session
    