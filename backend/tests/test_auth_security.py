"""Tests for authentication and security."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_helpers import create_test_user, create_admin_and_get_token, get_auth_token
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.security.auth import verify_password, get_password_hash


@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication flows."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["username"] == "newuser"
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient, db_session: AsyncSession):
        """Test registering with duplicate email."""
        # Create first user
        await create_test_user(db_session, "duplicate@test.com", "user1", "pass123", UserRole.USER)

        # Try to register with same email
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "duplicate@test.com",
                "username": "user2",
                "password": "pass123",
                "full_name": "User 2",
            },
        )
        assert response.status_code >= 400  # Should fail

    async def test_register_duplicate_username(self, client: AsyncClient, db_session: AsyncSession):
        """Test registering with duplicate username."""
        # Create first user
        await create_test_user(db_session, "user1@test.com", "sameusername", "pass123", UserRole.USER)

        # Try to register with same username
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "user2@test.com",
                "username": "sameusername",
                "password": "pass123",
                "full_name": "User 2",
            },
        )
        assert response.status_code >= 400  # Should fail

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registering with invalid email."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "username": "user",
                "password": "pass123",
                "full_name": "User",
            },
        )
        assert response.status_code == 422

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registering with weak password."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "user@test.com",
                "username": "user",
                "password": "123",  # Too short
                "full_name": "User",
            },
        )
        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful login."""
        # Create user
        await create_test_user(db_session, "login@test.com", "loginuser", "pass123", UserRole.USER)

        # Login
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "loginuser",
                "password": "pass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, db_session: AsyncSession):
        """Test login with wrong password."""
        # Create user
        await create_test_user(db_session, "user@test.com", "user", "correct_pass", UserRole.USER)

        # Try to login with wrong password
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "user",
                "password": "wrong_pass",
            },
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent username."""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "password",
            },
        )
        assert response.status_code == 401

    async def test_get_current_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting current user info."""
        # Create user and get token
        await create_test_user(db_session, "me@test.com", "meuser", "pass123", UserRole.USER)
        token = await get_auth_token(client, "meuser", "pass123")

        # Get current user
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "meuser"
        assert data["email"] == "me@test.com"

    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password hashing and verification."""

    def test_password_hashing(self):
        """Test that password hashing works."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 20

    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.asyncio
class TestAuthorization:
    """Test authorization and permissions."""

    async def test_user_cannot_access_admin_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test that regular user cannot access admin endpoints."""
        # Create regular user
        await create_test_user(db_session, "user@test.com", "regularuser", "pass123", UserRole.USER)
        token = await get_auth_token(client, "regularuser", "pass123")

        # Try to create ingredient (admin only)
        response = await client.post(
            "/api/ingredients/",
            json={"name": "Test", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_admin_can_access_admin_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test that admin can access admin endpoints."""
        admin_token = await create_admin_and_get_token(client, db_session)

        # Create ingredient (admin only)
        response = await client.post(
            "/api/ingredients/",
            json={"name": "Admin Test Ingredient", "unit": "kg"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201

    async def test_user_can_access_user_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test that regular user can access user endpoints."""
        # Create admin to set up product
        admin_token = await create_admin_and_get_token(client, db_session)

        # Create ingredient, recipe, and product
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "User Auth Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        ingredient_id = ing_response.json()["id"]

        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "User Auth Recipe",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        recipe_id = recipe_response.json()["id"]

        product_response = await client.post(
            "/api/products/",
            json={
                "name": "User Auth Product",
                "price": 10.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        product_id = product_response.json()["id"]

        # Create regular user
        await create_test_user(db_session, "orderuser@test.com", "orderuser", "pass123", UserRole.USER)
        user_token = await get_auth_token(client, "orderuser", "pass123")

        # User should be able to create order
        response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "User Customer",
                "customer_email": "customer@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201

    async def test_user_cannot_see_other_users_orders(self, client: AsyncClient, db_session: AsyncSession):
        """Test that user can only see their own orders."""
        # Create admin and product
        admin_token = await create_admin_and_get_token(client, db_session)

        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Privacy Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        ingredient_id = ing_response.json()["id"]

        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Privacy Recipe",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        recipe_id = recipe_response.json()["id"]

        product_response = await client.post(
            "/api/products/",
            json={
                "name": "Privacy Product",
                "price": 10.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        product_id = product_response.json()["id"]

        # Create two users
        await create_test_user(db_session, "user1@test.com", "user1", "pass123", UserRole.USER)
        await create_test_user(db_session, "user2@test.com", "user2", "pass123", UserRole.USER)

        user1_token = await get_auth_token(client, "user1", "pass123")
        user2_token = await get_auth_token(client, "user2", "pass123")

        # User 1 creates order
        user1_order = await client.post(
            "/api/orders/",
            json={
                "customer_name": "User 1",
                "customer_email": "user1order@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        order_id = user1_order.json()["id"]

        # User 2 tries to access User 1's order
        response = await client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response.status_code == 403

        # User 1 can access their own order
        response = await client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert response.status_code == 200

        # Admin can access any order
        response = await client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
