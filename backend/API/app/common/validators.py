from typing import Optional

from fastapi import HTTPException
from starlette import status

from app.auth.models.nn_user import NNUser
from app.content.models.content import Content


def validate_user_authenticated(user: Optional[NNUser]):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return True

def validate_content_owner(content: Content, owner: NNUser):
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content with this id does not exist",
        )
    if content.user_id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
        )
    return True