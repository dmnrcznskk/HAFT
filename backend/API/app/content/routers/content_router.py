from uuid import UUID

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends, File

from app.auth.models.nn_user import NNUser
from app.auth.routers.auth_router import get_current_user
from app.content.models.content import CreateContent
from app.content.services.content_service import ContentService
from app.core.dependencies import get_content_service

content_router = APIRouter()


@content_router.post("/create")
async def create_content(
    content: CreateContent,
    user: NNUser = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    saved_content = await content_service.save_content(content, user)
    return saved_content


@content_router.post("/{content_id}/embroidery/")
async def create_embroidery(
    content_id: UUID,
    file: UploadFile = File(...),
    user: NNUser = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    return await content_service.save_embroidery(content_id, file, user)


@content_router.get("/{content_id}/embroidery/")
async def get_embroidery(
    content_id: UUID,
    user: NNUser = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    return await content_service.get_embroidery_by_content_id(content_id, user)
