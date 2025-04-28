from fastapi import APIRouter

session_router = APIRouter()


@session_router.read('/session')
async def read_sessions():
    return {"Its working!": "Hellooo"}