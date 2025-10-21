"""User settings API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.user_settings_dto import (
    UpdateUserSettingsRequestDTO,
    UserSettingsResponseDTO,
)
from src.domain.entities.user import User
from src.domain.value_objects.user_settings import UserSettings
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.session import get_db
from src.presentation.api.dependencies import get_current_user

router = APIRouter()


@router.get("/me/settings", response_model=UserSettingsResponseDTO)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserSettingsResponseDTO:
    """Get current user's settings.

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        User settings

    Raises:
        HTTPException: If user not found
    """
    try:
        user_repo = UserRepository(session)
        settings = await user_repo.get_settings(current_user.id)
        return UserSettingsResponseDTO(preferred_language=settings.preferred_language)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Log the actual error for debugging
        import logging

        logging.error(f"Unexpected error getting user settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting user settings.",
        )


@router.patch("/me/settings", response_model=UserSettingsResponseDTO)
async def update_user_settings(
    dto: UpdateUserSettingsRequestDTO,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserSettingsResponseDTO:
    """Update current user's settings.

    Args:
        dto: Settings update data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated user settings

    Raises:
        HTTPException: If validation fails or user not found
    """
    try:
        user_repo = UserRepository(session)
        settings = UserSettings(preferred_language=dto.preferred_language)
        updated_user = await user_repo.update_settings(current_user.id, settings)
        await session.commit()
        return UserSettingsResponseDTO(preferred_language=updated_user.settings.preferred_language)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        # Log the actual error for debugging
        import logging

        logging.error(f"Unexpected error updating user settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating user settings.",
        )
