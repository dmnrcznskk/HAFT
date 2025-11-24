from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field


class NNUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str


class CreateNNUser(BaseModel):
    email: EmailStr
    password: str
