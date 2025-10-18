"""Unit tests for security modules."""
from datetime import datetime, timedelta

import pytest

from src.infrastructure.security.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from src.infrastructure.security.jwt import decode_token, get_user_id_from_token


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password(self):
        """Test hashing a password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        """Test verifying correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test verifying incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False


class TestJWT:
    """Test JWT token functions."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"user_id": 1, "role": "user"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"user_id": 1, "role": "admin"}
        token = create_access_token(data)

        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["user_id"] == 1
        assert decoded["role"] == "admin"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"

        decoded = decode_token(invalid_token)

        assert decoded is None

    def test_token_contains_expiration(self):
        """Test that token contains expiration claim."""
        from datetime import timedelta

        data = {"user_id": 1}
        token = create_access_token(data)

        decoded = decode_token(token)

        assert "exp" in decoded
        assert decoded["user_id"] == 1
        # Expiration time should be a number (Unix timestamp)
        assert isinstance(decoded["exp"], (int, float))

    def test_create_token_with_custom_expiration(self):
        """Test creating token with custom expiration."""
        data = {"user_id": 1}
        custom_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta=custom_delta)

        decoded = decode_token(token)

        assert decoded is not None
        assert "exp" in decoded
