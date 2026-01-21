import base64
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile, HTTPException
from starlette import status

from app.auth.models.nn_user import NNUser
from app.common.validators import validate_content_owner
from app.content.models.bucket import Bucket
from app.content.models.content import Content, CreateContent
from app.content.models.embroidery import Embroidery, ResponseEmbroideryContent
from app.content.repositories.content_repository import ContentRepository
from app.content.repositories.embroidery_repository import EmbroideryRepository
from app.content.services.storage_service import StorageService
import io

import sys

image_processing_path = str(
    Path(__file__).parent.parent.parent.parent / "image_processing"
)
if image_processing_path not in sys.path:
    sys.path.append(image_processing_path)

from image_processing.process_image import process_image


def _map_content_embroidery_list(embroider_list):
    return [
        ResponseEmbroideryContent(
            id=embroidery.content.id,
            content_type=embroidery.content.content_type,
            title=embroidery.content.title,
            text=embroidery.content.text,
            url=embroidery.url,
        )
        for embroidery in embroider_list
    ]


async def generate_embroidery_from_picture(
    img: UploadFile, num_colors: int, width_cm: int, aida_count: int
):
    image_bytes = await img.read()
    image_file = io.BytesIO(image_bytes)
    result = process_image(image_file, num_colors, width_cm, aida_count)

    preview_base64 = base64.b64encode(result["preview_png"].getvalue()).decode("utf-8")
    chart_base64 = base64.b64encode(result["chart_png"].getvalue()).decode("utf-8")

    response = {
        **result["pattern_data"],
        "preview_png": f"data:image/png;base64,{preview_base64}",
        "chart_png": f"data:image/png;base64,{chart_base64}",
    }

    return response


class ContentService:
    def __init__(
        self,
        embroidery_repo: EmbroideryRepository,
        content_repo: ContentRepository,
        storage_service: StorageService,
    ):
        self.embroidery_repo = embroidery_repo
        self.storage_service = storage_service
        self.content_repo = content_repo

    async def save_content(self, content: CreateContent, user: NNUser):
        content_to_save = Content(user_id=user.id, **content.model_dump())
        saved_content = await self.content_repo.create(content_to_save)

        return saved_content

    async def save_embroidery(self, content_id: UUID, file: UploadFile, user: NNUser):

        content = await self.content_repo.get_content_by_id(content_id)

        validate_content_owner(content, user)

        extension = Path(file.filename).suffix.lower()
        unique_id = uuid.uuid4()
        file_name = f"{unique_id}{extension}"

        url = await self.storage_service.save_img(file_name, Bucket.EMBROIDERY, file)

        return await self.embroidery_repo.create(
            Embroidery(content_id=content_id, url=url)
        )

    async def get_embroidery_by_content_id(self, content_id: UUID, user: NNUser = None):
        content = await self.content_repo.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content with this id does not exist",
            )

        if not content.is_public:
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )
            if user.id != content.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
                )

        if not content.embroidery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Embroidery not found"
            )
        return ResponseEmbroideryContent(
            **content.model_dump(), url=content.embroidery.url
        )

    async def get_private_library(self, user):
        embroideries = await self.embroidery_repo.get_embroideries_by_user_id(user.id)

        return _map_content_embroidery_list(embroideries)

    async def get_public_embroideries(self):
        embroideries = await self.embroidery_repo.get_public_embroideries()
        return _map_content_embroidery_list(embroideries)

    async def get_public_embroideries_of_user(self, user_id: UUID):
        embroideries = await self.embroidery_repo.get_public_embroideries_of_user(
            user_id
        )
        return _map_content_embroidery_list(embroideries)

    async def delete_embroidery(self, content_id: UUID, current_user: NNUser):
        content = await self.content_repo.get_content_by_id(content_id)
        embroidery = content.embroidery

        validate_content_owner(content, current_user)
        if not embroidery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Embroidery not found"
            )

        self.storage_service.delete(embroidery.url)
        await self.embroidery_repo.delete(embroidery)
        await self.content_repo.delete(content)
