import datetime
import uuid
from typing import Optional
from uuid import UUID
from sqlalchemy import Text, Column
from sqlmodel import SQLModel, Field
from app.models.content_type import ContentType


class ContentBase(SQLModel):
    content_type: ContentType
    title: str
    text: str = Field(sa_column=Column(Text))


class Content(ContentBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    createdAt: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updatedAt: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.datetime.now(datetime.UTC)},
    )
    user_id: UUID = Field(foreign_key="nn_user.id")


# class to keep code clean
class CreateContent(ContentBase):
    pass


class UpdateContent(ContentBase):
    title: Optional[str] = None
    text: Optional[str] = None
