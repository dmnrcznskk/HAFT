from typing import Optional

from fastapi import HTTPException

from app.auth.models.nn_user import NNUser


def validate_user_authenticated(user: Optional[NNUser]):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return True
