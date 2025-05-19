from fastapi import APIRouter, Depends
from typing import Annotated
from app.auths.dependency import admin_only
from app.models import UserInDb

admin_router = APIRouter()




@admin_router.post('/admin-only/', tags=['Admin'])
async def admin_only_endpoint(
    current_user: Annotated[UserInDb, Depends(admin_only)]
):
    return {"message": "You have admin access"}
