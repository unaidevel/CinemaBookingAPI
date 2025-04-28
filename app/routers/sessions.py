from fastapi import APIRouter

session_router = APIRouter()


@session_router.get('/session')
async def read_sessions():
    return {"Its working!": "Hellooo"}