import datetime
import uuid
from typing import Optional
from uuid import UUID
from sqlalchemy import Text, Column, DateTime
from sqlmodel import SQLModel, Field
from app.models.content_type import ContentType
from sqlalchemy import Enum as SAEnum


class ContentBase(SQLModel):
    content_type: ContentType = Field(
        sa_column=Column(
            SAEnum(ContentType, name="contenttype"),
            nullable=False,
        )
    )
    title: str
    text: str = Field(sa_column=Column(Text))


class Content(ContentBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    createdAt: datetime.datetime = Field(
        default_factory = datetime.datetime.now,
        sa_type=DateTime(timezone=True)
    )
    updatedAt: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"onupdate": datetime.datetime.now},
    )
    user_id: UUID = Field(foreign_key="nn_user.id")


# class to keep code clean
class CreateContent(ContentBase):
    pass


class UpdateContent(ContentBase):
    title: Optional[str] = None
    text: Optional[str] = None
