from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import Response

from app.core.config import settings
from app.core.dependencies import get_auth_service, get_current_user
from app.auth.models.nn_user import CreateNNUser, ResponseNNUser, NNUser
from app.auth.models.token import ReturnToken
from app.auth.services.auth_service import AuthService

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
        value=refresh_token.token_value,
        httponly=True,
        samesite="lax",
        secure=settings.IS_PRODUCTION,
    )
    return ReturnToken(access_token=access_token.token_value)


@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    auth_service: AuthService = Depends(get_auth_service),
    refresh_token: str = Cookie(None),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    new_token = await auth_service.refresh_session(refresh_token)
    return new_token


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie(
        key="refresh_token", httponly=True, secure=settings.IS_PRODUCTION
    )
    return {"message": "Logged out successfully"}


@auth_router.get("/me", response_model=ResponseNNUser, status_code=status.HTTP_200_OK)
async def get_current_user(
    current_user: NNUser = Depends(get_current_user)
):
    return current_user