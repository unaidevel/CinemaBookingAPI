from sqlmodel import SQLModel, Field
import uuid

class Sessions(SQLModel, table=True):
    id: uuid = Field(default_factory=uuid.uuid4)