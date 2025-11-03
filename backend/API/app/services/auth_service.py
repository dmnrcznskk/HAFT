from fastapi import HTTPException
from fastapi.openapi.utils import status_code_ranges
from pwdlib import PasswordHash
from starlette import status

from app.models.nn_user import CreateNNUser, NNUser


class AuthService:
    def __init__(self, repo):
        self.repo = repo
        self.password_hash = PasswordHash.recommended()

    async def register_user(self, new_user:CreateNNUser):
        existing_user = await self.repo.get_user_by_email(new_user.email)
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "User with this email already exists"
            )
        hashed_password = self.password_hash.hash(new_user.password)
        mapped_new_user = NNUser(email=new_user.email, hashed_password=hashed_password)

        return await self.repo.create_user(mapped_new_user)