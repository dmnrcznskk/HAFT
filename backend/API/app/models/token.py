from pydantic import BaseModel


class Token(BaseModel):
    token_value: str
    token_type: str
