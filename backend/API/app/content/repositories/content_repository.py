from uuid import UUID

from sqlalchemy.future import select
from sqlmodel import col

from app.common.repository_base import RepositoryBase
from app.content.models.content import Content
from sqlalchemy.orm import selectinload


class ContentRepository(RepositoryBase):
    async def get_content_by_id(self, content_id: UUID):
        query = (
            select(Content)
            .where(Content.id == content_id)
            .options(selectinload(Content.embroidery))
        )
        result = await self.db.exec(query)
        return result.scalar_one_or_none()

    async def get_content_list_by_title(self, search_phrase: str):
        query = select(Content).where(col(Content.title).ilike(f"{search_phrase}%"))
        existing_content = await self.db.exec(query)
        return existing_content.all()
