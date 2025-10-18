"""Login user use case."""
from src.application.dtos.auth_dto import LoginRequestDTO, TokenResponseDTO
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.security.auth import create_access_token, verify_password


class LoginUserUseCase:
    """Use case for user login."""

    def __init__(self, user_repository: IUserRepository):
        """Initialize use case with dependencies."""
        self._user_repo = user_repository

    async def execute(self, dto: LoginRequestDTO) -> TokenResponseDTO:
        """Execute user login.

        Args:
            dto: Login request data

        Returns:
            TokenResponseDTO with access token

        Raises:
            ValueError: If credentials are invalid
        """
        # Get user by username
        user = await self._user_repo.get_by_username(dto.username)

        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        if not verify_password(dto.password, user.hashed_password):
            raise ValueError("Invalid credentials")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is inactive")

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )

        return TokenResponseDTO(access_token=access_token)
