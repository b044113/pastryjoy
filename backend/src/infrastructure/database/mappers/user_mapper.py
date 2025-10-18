"""User mapper between database model and domain entity."""
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.models.user import UserModel


class UserMapper:
    """Maps between UserModel and User entity."""

    @staticmethod
    def to_entity(model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            is_active=model.is_active,
            full_name=model.full_name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Convert domain entity to database model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            hashed_password=entity.hashed_password,
            role=entity.role.value,
            is_active=entity.is_active,
            full_name=entity.full_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
