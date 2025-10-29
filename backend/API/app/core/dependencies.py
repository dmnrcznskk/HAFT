from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.session import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db=db)

def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo=repo)
