import datetime
import uuid
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Text, Column, DateTime
from sqlmodel import SQLModel, Field, Relationship

from app.content.models.content_type import ContentType

if TYPE_CHECKING:
    from app.content.models.embroidery import Embroidery


class ContentBase(SQLModel):
    content_type: ContentType = Field(
        sa_column=Column(
            SAEnum(ContentType, name="contenttype"),
            nullable=False,
        )
    )
    title: str
    text: str = Field(sa_column=Column(Text))
    is_public: bool = True


class Content(ContentBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"onupdate": datetime.datetime.now},
    )
    user_id: UUID = Field(foreign_key="nn_user.id")
    embroidery: Optional["Embroidery"] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
        },
    )


# class to keep code clean
class CreateContent(ContentBase):
    pass


class UpdateContent(ContentBase):
    title: Optional[str] = None
    text: Optional[str] = None
