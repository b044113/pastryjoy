"""Tests for API error handling and validation."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_helpers import create_admin_and_get_token, create_test_user, get_auth_token
from src.domain.value_objects.user_role import UserRole


@pytest.mark.asyncio
class TestAPIErrorHandling:
    """Test API error handling across different endpoints."""

    async def test_unauthorized_access_to_ingredients(self, client: AsyncClient):
        """Test accessing ingredients without token."""
        response = await client.get("/api/ingredients/")
        assert response.status_code == 401

    async def test_unauthorized_access_to_recipes(self, client: AsyncClient):
        """Test accessing recipes without token."""
        response = await client.get("/api/recipes/")
        assert response.status_code == 401

    async def test_unauthorized_access_to_products(self, client: AsyncClient):
        """Test accessing products without token."""
        response = await client.get("/api/products/")
        assert response.status_code == 401

    async def test_unauthorized_access_to_orders(self, client: AsyncClient):
        """Test accessing orders without token."""
        response = await client.get("/api/orders/")
        assert response.status_code == 401

    async def test_user_cannot_create_ingredients(self, client: AsyncClient, db_session: AsyncSession):
        """Test that regular user cannot create ingredients."""
        await create_test_user(db_session, "user@test.com", "regularuser", "pass123", UserRole.USER)
        token = await get_auth_token(client, "regularuser", "pass123")

        response = await client.post(
            "/api/ingredients/",
            json={"name": "Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    async def test_user_cannot_create_recipes(self, client: AsyncClient, db_session: AsyncSession):
        """Test that regular user cannot create recipes."""
        await create_test_user(db_session, "user@test.com", "regularuser", "pass123", UserRole.USER)
        token = await get_auth_token(client, "regularuser", "pass123")

        response = await client.post(
            "/api/recipes/",
            json={"name": "Test Recipe", "instructions": "Mix", "ingredients": []},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    async def test_user_cannot_create_products(self, client: AsyncClient, db_session: AsyncSession):
        """Test that regular user cannot create products."""
        await create_test_user(db_session, "user@test.com", "regularuser", "pass123", UserRole.USER)
        token = await get_auth_token(client, "regularuser", "pass123")

        response = await client.post(
            "/api/products/",
            json={"name": "Test Product", "recipes": []},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    async def test_invalid_ingredient_unit(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating ingredient with invalid unit."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/ingredients/",
            json={"name": "Test", "unit": "invalid_unit"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    async def test_duplicate_ingredient_name(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating ingredient with duplicate name."""
        token = await create_admin_and_get_token(client, db_session)

        # Create first ingredient
        await client.post(
            "/api/ingredients/",
            json={"name": "Unique Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try to create duplicate
        response = await client.post(
            "/api/ingredients/",
            json={"name": "Unique Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [400, 409, 422]  # Conflict or validation error

    async def test_missing_required_fields_ingredient(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating ingredient without required fields."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/ingredients/",
            json={"name": ""},  # Missing unit, empty name
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    async def test_missing_required_fields_recipe(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating recipe without required fields."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/recipes/",
            json={"name": ""},  # Empty name, missing ingredients
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    async def test_invalid_json_payload(self, client: AsyncClient, db_session: AsyncSession):
        """Test sending invalid JSON."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/ingredients/",
            content="invalid json",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 422

    async def test_invalid_token_format(self, client: AsyncClient):
        """Test using invalid token format."""
        response = await client.get(
            "/api/ingredients/",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401

    async def test_expired_or_malformed_token(self, client: AsyncClient):
        """Test using malformed token."""
        response = await client.get(
            "/api/ingredients/",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1.invalid.token"},
        )

        assert response.status_code == 401

    async def test_get_nonexistent_resource(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting non-existent ingredient."""
        from uuid import uuid4
        token = await create_admin_and_get_token(client, db_session)

        # Try to get a random UUID that doesn't exist
        fake_id = str(uuid4())
        response = await client.get(
            f"/api/ingredients/{fake_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    async def test_update_nonexistent_resource(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating non-existent ingredient."""
        from uuid import uuid4
        token = await create_admin_and_get_token(client, db_session)

        fake_id = str(uuid4())
        response = await client.put(
            f"/api/ingredients/{fake_id}",
            json={"name": "Updated", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    async def test_delete_nonexistent_resource(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting non-existent ingredient."""
        from uuid import uuid4
        token = await create_admin_and_get_token(client, db_session)

        fake_id = str(uuid4())
        response = await client.delete(
            f"/api/ingredients/{fake_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    async def test_admin_can_access_all_endpoints(self, client: AsyncClient, db_session: AsyncSession):
        """Test that admin can access all protected endpoints."""
        token = await create_admin_and_get_token(client, db_session)

        # Test all GET endpoints
        endpoints = [
            "/api/ingredients/",
            "/api/recipes/",
            "/api/products/",
            "/api/orders/",
        ]

        for endpoint in endpoints:
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200, f"Failed on {endpoint}"

    async def test_user_can_create_orders(self, client: AsyncClient, db_session: AsyncSession):
        """Test that regular user CAN create orders."""
        await create_test_user(db_session, "orderuser@test.com", "orderuser", "pass123", UserRole.USER)
        token = await get_auth_token(client, "orderuser", "pass123")

        # This should work (or return 422 for validation, but not 403 for auth)
        response = await client.post(
            "/api/orders/",
            json={"customer_name": "Test", "items": []},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should not be 403 (forbidden), can be 422 (validation error)
        assert response.status_code != 403
