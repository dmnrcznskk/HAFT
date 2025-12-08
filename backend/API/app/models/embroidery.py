from uuid import UUID

from sqlmodel import SQLModel, Field


class Embroidery(SQLModel, table=True):
    id: int = Field(primary_key=True)
    url: str
    content_id: UUID = Field(foreign_key="content.id")