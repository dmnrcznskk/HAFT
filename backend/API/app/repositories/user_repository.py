from sqlmodel import select

from app.models.nn_user import NNUser
from app.repositories.repository_base import RepositoryBase


class UserRepository(RepositoryBase):
    async def get_user_by_email(self, email: str):
        query = select(NNUser).where(NNUser.email == email)
        existing_user = await self.db.exec(query)
        return existing_user.first()
