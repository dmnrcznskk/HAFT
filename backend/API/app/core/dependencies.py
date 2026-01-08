from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.models.nn_user import NNUser
from app.auth.repositories.user_repository import UserRepository
from app.auth.services.auth_service import AuthService
from app.content.repositories.content_repository import ContentRepository
from app.content.repositories.embroidery_repository import EmbroideryRepository
from app.content.services.content_service import ContentService
from app.content.services.storage_service import StorageService
from app.core.session import get_session

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class GetRepo:
    def __init__(self, repo_type):
        self.repo_type = repo_type

    def __call__(self, db: AsyncSession = Depends(get_session)):
        return self.repo_type(db)


def get_auth_service(
    repo: UserRepository = Depends(GetRepo(UserRepository)),
) -> AuthService:
    return AuthService(repo=repo)


def get_content_service(
    content_repo: ContentRepository = Depends(GetRepo(ContentRepository)),
    embroidery_repo: EmbroideryRepository = Depends(GetRepo(EmbroideryRepository)),
) -> ContentService:
    return ContentService(
        content_repo=content_repo,
        embroidery_repo=embroidery_repo,
        storage_service=StorageService(),
    )


async def get_current_user(
    token: str = Depends(reusable_oauth2),
    service: AuthService = Depends(get_auth_service),
) -> NNUser | None:
    if not token:
        return None

    try:
        return await service.get_user_from_token(token)
    except HTTPException:
        return None
