"""Script to create an admin user."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.auth import get_password_hash
from src.infrastructure.config.settings import get_settings

settings = get_settings()


async def create_admin_user():
    """Create an admin user if it doesn't exist."""
    # Create database engine
    engine = create_async_engine(settings.database_url, echo=True)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        user_repo = UserRepository(session)

        # Check if admin user already exists
        admin_username = "admin"
        existing_user = await user_repo.get_by_username(admin_username)

        if existing_user:
            print(f"❌ Admin user '{admin_username}' already exists!")
            return

        # Create admin user
        admin_user = User(
            email="admin@pastryjoy.com",
            username=admin_username,
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            full_name="Administrator",
            is_active=True,
        )

        created_user = await user_repo.create(admin_user)
        await session.commit()

        print("\n✅ Admin user created successfully!")
        print(f"   Username: {created_user.username}")
        print(f"   Email: {created_user.email}")
        print(f"   Password: admin123")
        print(f"   Role: {created_user.role.value}")
        print("\n⚠️  Please change the password after first login!\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
