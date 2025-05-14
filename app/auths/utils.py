from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime, UTC
from pydantic import BaseModel
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models import UserInDb

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class TokenRefresh(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: uuid.UUID = Field(foreign_key='userindb.id')
    date_created: datetime = Field(default_factory= lambda: datetime.now(UTC))
    expires_at: datetime


    user: 'UserInDb' = Relationship(back_populates='refresh_tokens')

