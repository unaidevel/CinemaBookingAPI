from fastapi import APIRouter
from app.models import Session
session_router = APIRouter()


@session_router.post('/sessions')
async def create_session():
    pass