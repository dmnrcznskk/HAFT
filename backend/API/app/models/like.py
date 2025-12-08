import uuid

from sqlmodel import SQLModel, Field


class Like(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="nn_user.id")
    content_id: uuid.UUID = Field(foreign_key="content.id")