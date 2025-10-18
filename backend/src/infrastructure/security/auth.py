"""Authentication utilities."""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from ..config.settings import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password

    Raises:
        ValueError: If password is too long or invalid

    Note:
        Bcrypt has a maximum password length of 72 bytes. Passwords longer than
        this will be truncated to avoid errors.
    """
    # Truncate password to 72 bytes for bcrypt
    # This is a limitation of bcrypt algorithm
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')

    try:
        return pwd_context.hash(password)
    except Exception as e:
        # Handle bcrypt-specific errors
        error_msg = str(e)
        if "password" in error_msg.lower() and "72" in error_msg:
            raise ValueError("Password is too long. Please use a shorter password (max 72 characters).")
        raise ValueError(f"Password hashing failed: {error_msg}")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt
