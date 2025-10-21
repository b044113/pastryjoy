"""Authentication DTOs."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequestDTO(BaseModel):
    """Request DTO for user registration."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128, description="Password must be between 8 and 128 characters")
    full_name: str | None = Field(None, max_length=255)


class LoginRequestDTO(BaseModel):
    """Request DTO for user login."""

    username: str
    password: str


class TokenResponseDTO(BaseModel):
    """Response DTO for authentication token."""

    access_token: str
    token_type: str = "bearer"


class UserSettingsDTO(BaseModel):
    """Settings DTO for user data."""

    preferred_language: str


class UserResponseDTO(BaseModel):
    """Response DTO for user data."""

    id: UUID
    email: str
    username: str
    role: str
    is_active: bool
    full_name: str | None
    settings: UserSettingsDTO
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
