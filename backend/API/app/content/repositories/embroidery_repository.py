from uuid import UUID

from sqlalchemy.orm import joinedload
from sqlmodel import select

from app.common.repository_base import RepositoryBase
from app.content.models.content import Content
from app.content.models.embroidery import Embroidery


class EmbroideryRepository(RepositoryBase):
    async def get_embroidery_by_content_id(self, content_id: UUID):
        query = select(Embroidery).where(Embroidery.content_id == content_id)
        existing_embroidery = await self.db.exec(query)
        return existing_embroidery.all()

    async def get_embroideries_by_user_id(self, user_id: UUID):
        query = (
            select(Embroidery)
            .join(Content)
            .where(Content.user_id == user_id)
            .options(joinedload(Embroidery.content))
        )
        results = await self.db.exec(query)
        return results.all()

    async def get_public_embroideries(self):
        query = (
            select(Embroidery)
            .join(Content)
            .where(Content.is_public == True)
            .options(joinedload(Embroidery.content))
        )
        results = await self.db.exec(query)
        return results.all()

    async def get_public_embroideries_of_user(self, user_id: UUID):
        query = (
            select(Embroidery)
            .join(Content)
            .where(Content.is_public == True)
            .where(Content.user_id == user_id)
            .options(joinedload(Embroidery.content))
        )
        results = await self.db.exec(query)
        return results.all()
