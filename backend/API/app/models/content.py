import datetime
import uuid
from uuid import UUID
from sqlalchemy import Text, Column
from sqlmodel import SQLModel, Field
from app.models.content_type import ContentType


class Content(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content_type: ContentType
    createdAt: datetime.datetime
    updatedAt: datetime.datetime
    title: str
    text: str = Column(Text)
    user_id: UUID = Field(foreign_key="nn_user.id")
