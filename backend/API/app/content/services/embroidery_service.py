import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.auth.models.nn_user import NNUser
from app.content.models.bucket import Bucket
from app.content.models.embroidery import Embroidery
from app.content.repositories.embroidery_repository import EmbroideryRepository
from app.content.services.storage_service import StorageService


class EmbroideryService:
    def __init__(self, repo: EmbroideryRepository, storage_service: StorageService):
        self.repo = repo
        self.storage_service = storage_service

    async def save_embroidery(self, content_id: UUID, file: UploadFile, user: NNUser):

        extension = Path(file.filename).suffix.lower()
        unique_id = uuid.uuid4()
        file_name = f"{unique_id}{extension}"

        url = await self.storage_service.save_img(file_name, Bucket.EMBROIDERY, file)

        return await self.repo.create(
            Embroidery(content_id=content_id, url=url, user=user)
        )
