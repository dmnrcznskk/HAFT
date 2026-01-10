from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def create_token(
    data: dict, expires_delta: timedelta | None = None, token_type: str = "access"
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_payload(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if payload.get("sub") is None:
            raise credentials_exception

        return payload
    except jwt.InvalidTokenError:
        raise credentials_exception
