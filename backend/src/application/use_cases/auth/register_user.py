"""Register user use case."""
from src.application.dtos.auth_dto import RegisterRequestDTO, UserResponseDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import IUserRepository
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.security.auth import get_password_hash


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(self, user_repository: IUserRepository):
        """Initialize use case with dependencies."""
        self._user_repo = user_repository

    async def execute(self, dto: RegisterRequestDTO) -> UserResponseDTO:
        """Execute user registration.

        Args:
            dto: Registration request data

        Returns:
            UserResponseDTO with created user data

        Raises:
            ValueError: If email or username already exists
        """
        # Check if user already exists
        if await self._user_repo.email_exists(dto.email):
            raise ValueError("Email already registered")

        if await self._user_repo.username_exists(dto.username):
            raise ValueError("Username already taken")

        # Create user entity
        user = User(
            email=dto.email,
            username=dto.username,
            hashed_password=get_password_hash(dto.password),
            role=UserRole.USER,  # Default role
            full_name=dto.full_name,
        )

        # Save to database
        created_user = await self._user_repo.create(user)

        # Return response DTO
        return UserResponseDTO(
            id=created_user.id,
            email=created_user.email,
            username=created_user.username,
            role=created_user.role.value,
            is_active=created_user.is_active,
            full_name=created_user.full_name,
            created_at=created_user.created_at,
        )
