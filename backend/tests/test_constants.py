"""Test constants for credentials and test data.

This file centralizes all test credentials to avoid hardcoding them throughout test files.
These are ONLY for testing purposes and should NEVER be used in production.
"""
import os
import secrets
import string


def generate_test_password(length: int = 12) -> str:
    """Generate a random test password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# Test user credentials
class TestCredentials:
    """Centralized test credentials."""

    # Basic test user
    TEST_EMAIL = "test@example.com"
    TEST_USERNAME = "testuser"
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "TestPass123!")

    # Admin test user
    ADMIN_EMAIL = "admin@test.com"
    ADMIN_USERNAME = "adminuser"
    ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "AdminPass123!")

    # Alternative test users for specific scenarios
    TEST_EMAIL_2 = "test2@example.com"
    TEST_USERNAME_2 = "testuser2"

    # Duplicate testing
    DUPLICATE_EMAIL = "duplicate@example.com"
    DUPLICATE_USERNAME = "duplicateuser"

    # Login testing
    LOGIN_EMAIL = "login@example.com"
    LOGIN_USERNAME = "loginuser"

    # Inactive user testing
    INACTIVE_EMAIL = "inactive@example.com"
    INACTIVE_USERNAME = "inactiveuser"

    # Current user testing
    CURRENT_EMAIL = "current@example.com"
    CURRENT_USERNAME = "currentuser"

    # Flow testing
    FLOW_EMAIL = "flow@example.com"
    FLOW_USERNAME = "flowuser"

    # Wrong password for testing
    WRONG_PASSWORD = "WrongPass123!"

    # Invalid email for testing
    INVALID_EMAIL = "not-an-email"


# Database credentials (for documentation only - never hardcoded in actual config)
class DatabaseCredentials:
    """Database credentials - should only be used in documentation examples."""

    # Example PostgreSQL connection (DO NOT USE IN PRODUCTION)
    EXAMPLE_DB_USER = "pastryjoy_user"
    EXAMPLE_DB_PASSWORD = "use_strong_password_here"
    EXAMPLE_DB_HOST = "localhost"
    EXAMPLE_DB_PORT = "5432"
    EXAMPLE_DB_NAME = "pastryjoy_db"

    @staticmethod
    def get_example_connection_string() -> str:
        """Get an example connection string for documentation."""
        return (
            f"postgresql+asyncpg://{DatabaseCredentials.EXAMPLE_DB_USER}:"
            f"{DatabaseCredentials.EXAMPLE_DB_PASSWORD}@"
            f"{DatabaseCredentials.EXAMPLE_DB_HOST}:"
            f"{DatabaseCredentials.EXAMPLE_DB_PORT}/"
            f"{DatabaseCredentials.EXAMPLE_DB_NAME}"
        )


# API Testing
class APITestConstants:
    """Constants for API testing."""

    TEST_ORIGIN = "http://localhost:5173"
    TEST_HOST = "http://test"

    # Token expiration for testing (in seconds)
    TEST_TOKEN_EXPIRATION = 3600  # 1 hour
