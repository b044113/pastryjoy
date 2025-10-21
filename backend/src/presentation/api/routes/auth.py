"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.auth_dto import (
    LoginRequestDTO,
    RegisterRequestDTO,
    TokenResponseDTO,
    UserResponseDTO,
    UserSettingsDTO,
)
from src.application.use_cases.auth.login_user import LoginUserUseCase
from src.application.use_cases.auth.register_user import RegisterUserUseCase
from src.domain.entities.user import User
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.session import get_db
from src.presentation.api.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(
    dto: RegisterRequestDTO,
    session: AsyncSession = Depends(get_db),
) -> UserResponseDTO:
    """Register a new user.

    Args:
        dto: User registration data
        session: Database session

    Returns:
        Created user data

    Raises:
        HTTPException: If email or username already exists or validation fails
    """
    try:
        user_repo = UserRepository(session)
        use_case = RegisterUserUseCase(user_repo)
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logging.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration. Please try again later.",
        )


@router.post("/login", response_model=TokenResponseDTO)
async def login(
    dto: LoginRequestDTO,
    session: AsyncSession = Depends(get_db),
) -> TokenResponseDTO:
    """Login and get access token.

    Args:
        dto: Login credentials
        session: Database session

    Returns:
        Access token

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        user_repo = UserRepository(session)
        use_case = LoginUserUseCase(user_repo)
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logging.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login. Please try again later.",
        )


@router.get("/me", response_model=UserResponseDTO)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponseDTO:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return UserResponseDTO(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role.value,
        is_active=current_user.is_active,
        full_name=current_user.full_name,
        settings=UserSettingsDTO(preferred_language=current_user.settings.preferred_language),
        created_at=current_user.created_at,
    )
