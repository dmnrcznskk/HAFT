from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import Response

from app.core.config import settings
from app.core.dependencies import get_auth_service
from app.models.nn_user import CreateNNUser
from app.services.auth_service import AuthService

auth_router = APIRouter()


@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(
    new_user: CreateNNUser, auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.register_user(new_user)
    return {"message": "User created successfully"}


@auth_router.post("/token/", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token, refresh_token = await auth_service.login_user(
        form_data.username, form_data.password
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token.access_token,
        httponly=True,
        secure=settings.IS_PRODUCTION,
    )
    return access_token


@auth_router.post("/refresh/")
async def refresh_token(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    refresh_token: str = Cookie(None),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    print(refresh_token)

    new_token = await auth_service.refresh_session(refresh_token)
    return new_token