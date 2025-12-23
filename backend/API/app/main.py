from fastapi import FastAPI
from sqlmodel import SQLModel
from app.models.content import Content
from app.models.embroidery import Embroidery

from app.core.session import async_engine
from app.routers.auth_router import auth_router
from contextlib import asynccontextmanager
from app.routers.content_router import content_router


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

api = FastAPI(lifespan=lifespan)
api.include_router(auth_router, prefix="/auth", tags=["Authorization"])
api.include_router(content_router, prefix="/content", tags=["Content"])
