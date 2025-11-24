from fastapi import APIRouter
from fastapi.params import Depends
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
