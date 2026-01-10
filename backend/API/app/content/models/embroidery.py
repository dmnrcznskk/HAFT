from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import SQLModel, Field, Relationship

from app.content.models.content import Content, ContentBase

if TYPE_CHECKING:
    from app.content.models.content import Content


class Embroidery(SQLModel, table=True):
    id: int = Field(primary_key=True)
    url: str
    content_id: UUID = Field(foreign_key="content.id")
    content: "Content" = Relationship(back_populates="embroidery")


class ResponseEmbroideryContent(ContentBase):
    id: UUID
    url: str
