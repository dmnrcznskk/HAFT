from typing import Optional
from uuid import UUID

from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.params import Depends, File
from sqlalchemy.sql.functions import current_user

from app.auth.models.nn_user import NNUser
from app.auth.routers.auth_router import get_current_user
from app.common.validators import validate_user_authenticated
from app.content.models.content import CreateContent
from app.content.services import content_service
from app.content.services.content_service import (
    ContentService,
    generate_embroidery_from_picture,
)
from app.core.dependencies import get_content_service

content_router = APIRouter()


@content_router.post("/create")
async def create_content(
    content: CreateContent,
    current_user: NNUser = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    validate_user_authenticated(current_user)

    saved_content = await content_service.save_content(content, current_user)
    return saved_content


@content_router.post("/{content_id}/embroidery/")
async def create_embroidery(
    content_id: UUID,
    file: UploadFile = File(...),
    current_user: NNUser = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    validate_user_authenticated(current_user)

    return await content_service.save_embroidery(content_id, file, current_user)


@content_router.get("/{content_id}/embroidery/")
async def get_embroidery(
    content_id: UUID,
    current_user: Optional[NNUser] = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    return await content_service.get_embroidery_by_content_id(content_id, current_user)


@content_router.get("/library/private")
async def get_private_library(
    current_user: NNUser = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    validate_user_authenticated(current_user)

    return await content_service.get_private_library(current_user)


@content_router.get("/library/public")
async def get_public_embroideries(
    content_service: ContentService = Depends(get_content_service),
):
    return await content_service.get_public_embroideries()


@content_router.get("/library/public/user/{user_id}")
async def get_public_embroideries_of_user(
    user_id: UUID, content_service: ContentService = Depends(get_content_service)
):
    return await content_service.get_public_embroideries_of_user(user_id)


@content_router.post("/embroidery/generate")
async def generate_embroidery(
    num_colors: int, width_cm: int, aida_count: int, img: UploadFile = File(...)
):
    return await generate_embroidery_from_picture(img, num_colors, width_cm, aida_count)


@content_router.patch("/{content_id}/embroidery/update")
async def update_embroidery(
    content_id: UUID,
    file: UploadFile = File(...),
    current_user: NNUser = Depends(get_current_user),
):
    validate_user_authenticated(current_user)

    return await content_service.update_embroidery(content_id, file, current_user)
