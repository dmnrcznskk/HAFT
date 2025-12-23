from pydantic import BaseModel, Field


class Token(BaseModel):
    token_value: str = Field(serialization_alias="access_token")
    token_type: str = Field(default="bearer")

#This class is used to return the token to the user - Swagger UI needs it to for authentication to work correctly
class ReturnToken(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")