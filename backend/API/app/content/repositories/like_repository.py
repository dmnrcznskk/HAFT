from uuid import UUID

from sqlmodel import select

from app.common.repository_base import RepositoryBase
from app.content.models.like import Like


class LikeRepository(RepositoryBase):
    async def get_likes_by_content_id(self, content_id: UUID):
        query = select(Like).where(Like.content_id == content_id)
        existing_likes = await self.db.exec(query)
        return existing_likes.all()