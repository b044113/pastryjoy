"""Tests for products endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_helpers import create_admin_and_get_token


@pytest.mark.asyncio
class TestProducts:
    """Test products CRUD endpoints."""

    async def create_recipe(self, client: AsyncClient, token: str) -> int:
        """Helper to create a recipe with ingredients."""
        # Create ingredient
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Simple Dough",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        return recipe_response.json()["id"]

    async def test_create_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating a product successfully."""
        token = await create_admin_and_get_token(client, db_session)
        recipe_id = await self.create_recipe(client, token)

        response = await client.post(
            "/api/products/",
            json={
                "name": "Bread Loaf",
                "price": 5.99,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Bread Loaf"
        assert data["price"] == 5.99
        assert len(data["recipes"]) == 1

    async def test_create_product_unauthorized(self, client: AsyncClient):
        """Test creating product without authentication."""
        response = await client.post(
            "/api/products/",
            json={
                "name": "Test Product",
                "price": 10.0,
                "recipes": [],
            },
        )

        assert response.status_code == 401

    async def test_get_all_products(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting all products."""
        token = await create_admin_and_get_token(client, db_session)
        recipe_id = await self.create_recipe(client, token)

        # Create product
        await client.post(
            "/api/products/",
            json={
                "name": "Croissant",
                "price": 3.50,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            "/api/products/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_product_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting a specific product by ID."""
        token = await create_admin_and_get_token(client, db_session)
        recipe_id = await self.create_recipe(client, token)

        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Baguette",
                "price": 4.25,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        response = await client.get(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Baguette"

    async def test_update_product(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating a product."""
        token = await create_admin_and_get_token(client, db_session)
        recipe_id = await self.create_recipe(client, token)

        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Original Product",
                "price": 5.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        response = await client.put(
            f"/api/products/{product_id}",
            json={
                "name": "Updated Product",
                "price": 7.50,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 7.50

    async def test_delete_product(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting a product."""
        token = await create_admin_and_get_token(client, db_session)
        recipe_id = await self.create_recipe(client, token)

        create_response = await client.post(
            "/api/products/",
            json={
                "name": "To Delete",
                "price": 1.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == 404
