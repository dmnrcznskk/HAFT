import uuid

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from uuid import UUID

class NNUser(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str


class CreateNNUser(BaseModel):
    email: EmailStr
    password: str

class ResponseNNUser(BaseModel):
    id: UUID
    email: str