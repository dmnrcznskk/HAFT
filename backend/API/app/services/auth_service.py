from datetime import timedelta
from fastapi import HTTPException
from pwdlib import PasswordHash
from starlette import status
from app.models.nn_user import CreateNNUser, NNUser, ResponseNNUser
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
        mapped_new_user = NNUser(
            email=new_user.email, hashed_password=hashed_password, username="New User"
        )

        return await self.repo.create(mapped_new_user)

    async def _get_user_from_token(self, token: str):
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

    async def get_response_user_from_token(self, token: str):
        user = await self._get_user_from_token(token)
        return ResponseNNUser(**user.dict())

    async def login_user(self, email: str, password: str):
        user = await self.repo.get_user_by_email(email)

        if not user or not self.password_hash.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token = Token(
            token_value=security.create_token({"sub": user.email}), token_type="access"
        )
        refresh_token = Token(
            token_value=security.create_token(
                {"sub": user.email}, expires_delta=timedelta(days=7)
            ),
            token_type="refresh",
        )
        return access_token, refresh_token

    async def refresh_session(self, refresh_token: str):
        user = await self._get_user_from_token(refresh_token)
        new_access_token = Token(
            token_value=security.create_token({"sub": user.email}), token_type="access"
        )

        return new_access_token
