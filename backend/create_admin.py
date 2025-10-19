"""Script to create an admin user with a secure random password."""
import asyncio
import secrets
import string
import sys
from getpass import getpass
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.auth import get_password_hash
from src.infrastructure.config.settings import get_settings

settings = get_settings()


def generate_secure_password(length: int = 16) -> str:
    """Generate a cryptographically secure random password.

    Args:
        length: Length of the password (default: 16)

    Returns:
        Secure random password
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Ensure at least one of each type
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]
    # Fill the rest
    password.extend(secrets.choice(alphabet) for _ in range(length - 4))
    # Shuffle
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


async def create_admin_user():
    """Create an admin user if it doesn't exist."""
    print("═══════════════════════════════════")
    print("  PastryJoy Admin User Creator")
    print("═══════════════════════════════════\n")

    # Get user input
    admin_username = input("Enter admin username (default: admin): ").strip() or "admin"
    admin_email = input("Enter admin email (default: admin@pastryjoy.com): ").strip() or "admin@pastryjoy.com"
    admin_full_name = input("Enter admin full name (default: Administrator): ").strip() or "Administrator"

    # Ask for password input method
    print("\nPassword options:")
    print("1. Let the system generate a secure random password (recommended)")
    print("2. Enter your own password")
    choice = input("Choose option (1 or 2): ").strip()

    if choice == "2":
        # Manual password entry
        password = getpass("Enter password: ")
        password_confirm = getpass("Confirm password: ")

        if password != password_confirm:
            print("\n❌ Passwords do not match!")
            sys.exit(1)

        if len(password) < 8:
            print("\n❌ Password must be at least 8 characters long!")
            sys.exit(1)
    else:
        # Generate secure random password
        password = generate_secure_password()
        print("\n✅ Secure random password generated!")

    # Create database engine
    engine = create_async_engine(settings.database_url, echo=False)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        user_repo = UserRepository(session)

        # Check if admin user already exists
        existing_user = await user_repo.get_by_username(admin_username)

        if existing_user:
            print(f"\n❌ User '{admin_username}' already exists!")
            await engine.dispose()
            return

        # Check if email already exists
        existing_email = await user_repo.get_by_email(admin_email)
        if existing_email:
            print(f"\n❌ Email '{admin_email}' is already registered!")
            await engine.dispose()
            return

        # Create admin user
        admin_user = User(
            email=admin_email,
            username=admin_username,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            full_name=admin_full_name,
            is_active=True,
        )

        created_user = await user_repo.create(admin_user)
        await session.commit()

        print("\n✅ Admin user created successfully!")
        print("═══════════════════════════════════")
        print(f"   Username: {created_user.username}")
        print(f"   Email: {created_user.email}")
        print(f"   Full Name: {created_user.full_name}")
        print(f"   Password: {password}")
        print(f"   Role: {created_user.role.value}")
        print("═══════════════════════════════════")
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("   1. Save this password securely - it will not be shown again!")
        print("   2. Consider changing the password after first login")
        print("   3. Never share this password or commit it to version control\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
