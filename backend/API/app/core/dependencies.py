from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.session import get_session
from app.models.nn_user import NNUser
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")

class GetRepo:
    def __init__(self, repo_type):
        self.repo_type = repo_type

    def __call__(self, db: AsyncSession = Depends(get_session)):
        return self.repo_type(db)

def get_auth_service(
    repo: UserRepository = Depends(GetRepo(UserRepository)),
) -> AuthService:
    return AuthService(repo=repo)

async def get_current_user(
    token: str = Depends(reusable_oauth2),
    service: AuthService = Depends(get_auth_service),
) -> NNUser:
    return await service.get_user_from_token(token)
