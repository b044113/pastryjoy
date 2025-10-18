"""Tests for recipes endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_helpers import create_admin_and_get_token


@pytest.mark.asyncio
class TestRecipes:
    """Test recipes CRUD endpoints."""

    async def create_ingredient(self, client: AsyncClient, token: str, name: str, unit: str) -> int:
        """Helper to create an ingredient."""
        response = await client.post(
            "/api/ingredients/",
            json={"name": name, "unit": unit},
            headers={"Authorization": f"Bearer {token}"},
        )
        return response.json()["id"]

    async def test_create_recipe_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating a recipe successfully."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredients first
        flour_id = await self.create_ingredient(client, token, "Flour", "kg")
        sugar_id = await self.create_ingredient(client, token, "Sugar", "kg")

        response = await client.post(
            "/api/recipes/",
            json={
                "name": "Simple Bread",
                "instructions": "Mix and bake",
                "ingredients": [
                    {"ingredient_id": flour_id, "quantity": 0.5},
                    {"ingredient_id": sugar_id, "quantity": 0.1},
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Simple Bread"
        assert data["instructions"] == "Mix and bake"
        assert len(data["ingredients"]) == 2

    async def test_create_recipe_unauthorized(self, client: AsyncClient):
        """Test creating recipe without authentication."""
        response = await client.post(
            "/api/recipes/",
            json={
                "name": "Test Recipe",
                "instructions": "Test",
                "ingredients": [],
            },
        )

        assert response.status_code == 401

    async def test_get_all_recipes(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting all recipes."""
        token = await create_admin_and_get_token(client, db_session)

        flour_id = await self.create_ingredient(client, token, "Flour", "kg")

        # Create recipes
        await client.post(
            "/api/recipes/",
            json={
                "name": "Bread",
                "instructions": "Mix and bake",
                "ingredients": [{"ingredient_id": flour_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            "/api/recipes/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_recipe_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting a specific recipe by ID."""
        token = await create_admin_and_get_token(client, db_session)

        flour_id = await self.create_ingredient(client, token, "Flour", "kg")

        create_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Cake",
                "instructions": "Bake at 180°C",
                "ingredients": [{"ingredient_id": flour_id, "quantity": 0.3}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = create_response.json()["id"]

        response = await client.get(
            f"/api/recipes/{recipe_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recipe_id
        assert data["name"] == "Cake"

    async def test_update_recipe(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating a recipe."""
        token = await create_admin_and_get_token(client, db_session)

        flour_id = await self.create_ingredient(client, token, "Flour", "kg")

        create_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Original Name",
                "instructions": "Original instructions",
                "ingredients": [{"ingredient_id": flour_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = create_response.json()["id"]

        response = await client.put(
            f"/api/recipes/{recipe_id}",
            json={
                "name": "Updated Name",
                "instructions": "Updated instructions",
                "ingredients": [{"ingredient_id": flour_id, "quantity": 0.6}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["instructions"] == "Updated instructions"

    async def test_delete_recipe(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting a recipe."""
        token = await create_admin_and_get_token(client, db_session)

        flour_id = await self.create_ingredient(client, token, "Flour", "kg")

        create_response = await client.post(
            "/api/recipes/",
            json={
                "name": "To Delete",
                "instructions": "Will be deleted",
                "ingredients": [{"ingredient_id": flour_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/recipes/{recipe_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(
            f"/api/recipes/{recipe_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == 404
