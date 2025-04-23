from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime



class TokenRefresh(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: uuid.UUID = Field(foreign_key='userindb.id')
    date_created: datetime = Field(default=datetime.now())