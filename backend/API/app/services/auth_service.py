from datetime import timedelta
from fastapi import HTTPException
from pwdlib import PasswordHash
from starlette import status
from app.models.nn_user import CreateNNUser, NNUser
import app.core.security as security
from app.models.token import Token


class AuthService:
    def __init__(self, repo):
        self.repo = repo
        self.password_hash = PasswordHash.recommended()

    async def register_user(self, new_user: CreateNNUser):
        existing_user = await self.repo.get_user_by_email(new_user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        hashed_password = self.password_hash.hash(new_user.password)
        mapped_new_user = NNUser(email=new_user.email, hashed_password=hashed_password)

        return await self.repo.create_user(mapped_new_user)

    async def get_user_from_token(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = security.get_payload(token, credentials_exception)
            email = payload.get("sub")
            user = await self.repo.get_user_by_email(email)
        except Exception as e:
            raise credentials_exception

        if user is None:
            raise credentials_exception
        return user

    async def login_user(self, email: str, password: str):
        user = await self.repo.get_user_by_email(email)

        if not user or not self.password_hash.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token = Token(
            access_token=security.create_token({"sub": user.email}), token_type="bearer"
        )
        refresh_token = Token(
            access_token=security.create_token(
                {"sub": user.email}, expires_delta=timedelta(days=7)
            ),
            token_type="bearer",
        )
        return access_token, refresh_token
