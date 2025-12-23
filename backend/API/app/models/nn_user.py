import uuid

from pydantic import EmailStr
from sqlmodel import SQLModel, Field
from uuid import UUID


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    username: str | None = None


class NNUser(UserBase, table=True):
    __tablename__ = "nn_user"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str


class CreateNNUser(UserBase):
    password: str


class ResponseNNUser(UserBase):
    id: UUID
