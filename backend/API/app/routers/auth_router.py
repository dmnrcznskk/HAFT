from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from app.core.dependencies import get_auth_service
from app.models.nn_user import CreateNNUser
from app.services.auth_service import AuthService

auth_router = APIRouter()


@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(new_user: CreateNNUser, auth_service: AuthService = Depends(get_auth_service)):
    await auth_service.register_user(new_user)
    return {"message": "User created successfully"}
