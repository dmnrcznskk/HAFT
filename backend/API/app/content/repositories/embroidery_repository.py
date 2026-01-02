from uuid import UUID

from sqlmodel import select

from app.common.repository_base import RepositoryBase
from app.content.models.embroidery import Embroidery


class EmbroideryRepository(RepositoryBase):
    async def get_embroidery_by_content_id(self, content_id: UUID):
        query = select(Embroidery).where(Embroidery.content_id == content_id)
        existing_embroidery = await self.db.exec(query)
        return existing_embroidery.all()