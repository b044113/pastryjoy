"""Tests for ingredients endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_helpers import create_admin_and_get_token


@pytest.mark.asyncio
class TestIngredients:
    """Test ingredients CRUD endpoints."""

    async def test_create_ingredient_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating an ingredient successfully."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/ingredients/",
            json={"name": "Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Flour"
        assert data["unit"] == "kg"
        assert "id" in data

    async def test_create_ingredient_unauthorized(self, client: AsyncClient):
        """Test creating ingredient without authentication."""
        response = await client.post(
            "/api/ingredients/",
            json={"name": "Flour", "unit": "kg"},
        )

        assert response.status_code == 401

    async def test_get_all_ingredients(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting all ingredients."""
        token = await create_admin_and_get_token(client, db_session)

        # Create some ingredients
        await client.post(
            "/api/ingredients/",
            json={"name": "Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            "/api/ingredients/",
            json={"name": "Sugar", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Get all
        response = await client.get(
            "/api/ingredients/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert any(i["name"] == "Flour" for i in data)
        assert any(i["name"] == "Sugar" for i in data)

    async def test_get_ingredient_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting a specific ingredient by ID."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        create_response = await client.post(
            "/api/ingredients/",
            json={"name": "Butter", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = create_response.json()["id"]

        # Get by ID
        response = await client.get(
            f"/api/ingredients/{ingredient_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ingredient_id
        assert data["name"] == "Butter"

    async def test_get_ingredient_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting non-existent ingredient."""
        token = await create_admin_and_get_token(client, db_session)

        # First create an ingredient to get a valid ID, then delete it
        create_response = await client.post(
            "/api/ingredients/",
            json={"name": "Temporary", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        temp_id = create_response.json()["id"]

        await client.delete(
            f"/api/ingredients/{temp_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Now try to get the deleted ingredient
        response = await client.get(
            f"/api/ingredients/{temp_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    async def test_update_ingredient(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating an ingredient."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        create_response = await client.post(
            "/api/ingredients/",
            json={"name": "Eggs", "unit": "unit"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = create_response.json()["id"]

        # Update
        response = await client.put(
            f"/api/ingredients/{ingredient_id}",
            json={"name": "Large Eggs", "unit": "unit"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Large Eggs"

    async def test_delete_ingredient(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting an ingredient."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        create_response = await client.post(
            "/api/ingredients/",
            json={"name": "Salt", "unit": "g"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = create_response.json()["id"]

        # Delete
        response = await client.delete(
            f"/api/ingredients/{ingredient_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(
            f"/api/ingredients/{ingredient_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == 404

    async def test_create_ingredient_invalid_unit(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating ingredient with invalid unit."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/ingredients/",
            json={"name": "Test", "unit": "invalid_unit"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
