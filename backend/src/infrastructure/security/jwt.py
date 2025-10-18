"""JWT token handling."""
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt

from ..config.settings import get_settings

settings = get_settings()


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[UUID]:
    """Extract user ID from JWT token."""
    payload = decode_token(token)
    if payload is None:
        return None

    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        return None

    try:
        return UUID(user_id_str)
    except (ValueError, AttributeError):
        return None
