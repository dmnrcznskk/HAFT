
import bcrypt
from fastapi import HTTPException
from fastapi.openapi.utils import status_code_ranges
from starlette import status

from app.models.nn_user import CreateNNUser, NNUser


class AuthService:
    def __init__(self, repo):
        self.repo = repo

    async def register_user(self, new_user:CreateNNUser):
        existing_user = await self.repo.get_user_by_email(new_user.email)
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "User with this email already exists"
            )

        byte_password = new_user.password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(byte_password, salt)
        hashed_password_str = hashed_password.decode('utf-8')

        mapped_new_user = NNUser(email=new_user.email, hashed_password=hashed_password_str)

        return await self.repo.create_user(mapped_new_user)