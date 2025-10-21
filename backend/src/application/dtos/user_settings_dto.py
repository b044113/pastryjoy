"""User settings DTOs."""
from pydantic import BaseModel, Field


class UserSettingsResponseDTO(BaseModel):
    """User settings response DTO."""

    preferred_language: str = Field(..., pattern="^(en|es)$", description="User's preferred language (en or es)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UpdateUserSettingsRequestDTO(BaseModel):
    """Update user settings request DTO."""

    preferred_language: str = Field(..., pattern="^(en|es)$", description="User's preferred language (en or es)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
