from fastapi import FastAPI
from sqlmodel import SQLModel

from app.core.session import async_engine
from app.routers.auth_router import auth_router
from contextlib import asynccontextmanager


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

    print("Closing app")


api = FastAPI(lifespan=lifespan)
api.include_router(auth_router, prefix="/auth", tags=["Authorization", "Users"])
