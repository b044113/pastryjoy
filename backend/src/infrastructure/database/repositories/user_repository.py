"""User repository implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.database.mappers.user_mapper import UserMapper
from src.infrastructure.database.models.user import UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self._session = session

    async def create(self, entity: User) -> User:
        """Create a new user."""
        model = UserMapper.to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)

    async def get_by_id(self, entity_id: UUID) -> Optional[User]:
        """Get user by ID."""
        stmt = select(UserModel).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [UserMapper.to_entity(model) for model in models]

    async def update(self, entity: User) -> User:
        """Update an existing user."""
        stmt = select(UserModel).where(UserModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        # Update fields
        model.email = entity.email
        model.username = entity.username
        model.hashed_password = entity.hashed_password
        model.role = entity.role.value
        model.is_active = entity.is_active
        model.full_name = entity.full_name
        model.updated_at = entity.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)

    async def delete(self, entity_id: UUID) -> bool:
        """Delete a user by ID."""
        stmt = select(UserModel).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, entity_id: UUID) -> bool:
        """Check if user exists."""
        stmt = select(UserModel.id).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        stmt = select(UserModel.id).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
