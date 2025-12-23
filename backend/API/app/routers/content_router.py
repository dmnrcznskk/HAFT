from uuid import UUID

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends, File

from app.core.dependencies import get_content_service, get_embroidery_service
from app.models.content import CreateContent
from app.models.nn_user import NNUser
from app.routers.auth_router import get_current_user
from app.services.content_service import ContentService
from app.services.embroidery_service import EmbroideryService

content_router = APIRouter()


@content_router.post("/create")
async def create_content(
    content: CreateContent,
    user: NNUser = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    saved_content = await content_service.save_content(content, user)
    return saved_content


@content_router.post("/embroidery/{content_id}")
async def create_embroidery(
    content_id: UUID,
    file: UploadFile = File(...),
    user: NNUser = Depends(get_current_user),
    embroidery_service: EmbroideryService = Depends(get_embroidery_service),
):
    return await embroidery_service.save_embroidery(content_id, file, user)

