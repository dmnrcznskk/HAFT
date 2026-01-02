from uuid import UUID

from sqlmodel import select, col

from app.models.content import Content
from app.common.repository_base import RepositoryBase


class ContentRepository(RepositoryBase):
    async def get_content_by_id(self, id: UUID):
        query = select(Content).where(Content.id == id)
        existing_content = await self.db.exec(query)
        return existing_content.first()

    async def get_content_list_by_title(self, search_phrase: str):
        query = select(Content).where(col(Content.title).ilike(f"{search_phrase}%"))
        existing_content = await self.db.exec(query)
        return existing_content.all()