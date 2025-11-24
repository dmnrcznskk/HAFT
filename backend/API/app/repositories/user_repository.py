from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.nn_user import NNUser


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, new_user: NNUser):
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_email(self, email: str):
        query = select(NNUser).where(NNUser.email == email)
        existing_user = await self.db.exec(query)
        return existing_user.first()
