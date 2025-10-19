"""Tests for products endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_helpers import create_admin_and_get_token


@pytest.mark.asyncio
class TestProducts:
    """Test products CRUD endpoints."""

    async def create_recipe(self, client: AsyncClient, token: str, name: str = "Simple Dough") -> str:
        """Helper to create a recipe with ingredients."""
        # Create ingredient
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": f"Flour for {name}", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": name,
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": "0.5"}],
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
                "image_url": "https://example.com/bread.jpg",
                "fixed_costs": "5.99",
                "variable_costs_percentage": "10.5",
                "profit_margin_percentage": "20.0",
                "recipes": [{"recipe_id": recipe_id, "quantity": "1.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Bread Loaf"
        assert data["fixed_costs"] == "5.99"
        assert len(data["recipes"]) == 1

    async def test_create_product_unauthorized(self, client: AsyncClient):
        """Test creating product without authentication."""
        response = await client.post(
            "/api/products/",
            json={
                "name": "Test Product",
                "fixed_costs": "10.0",
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
                "fixed_costs": "3.50",
                "recipes": [{"recipe_id": recipe_id, "quantity": "1.0"}],
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
                "fixed_costs": "4.25",
                "recipes": [{"recipe_id": recipe_id, "quantity": "1.0"}],
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
                "fixed_costs": "5.0",
                "recipes": [{"recipe_id": recipe_id, "quantity": "1.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        response = await client.put(
            f"/api/products/{product_id}",
            json={
                "name": "Updated Product",
                "fixed_costs": "7.50",
                "recipes": [{"recipe_id": recipe_id, "quantity": "1.5"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["fixed_costs"] == "7.50"

    async def test_update_product_add_recipes(self, client: AsyncClient, db_session: AsyncSession):
        """Test adding recipes to an existing product - verifies bug fix."""
        token = await create_admin_and_get_token(client, db_session)
        recipe1_id = await self.create_recipe(client, token, "Recipe 1")

        # Create product with one recipe
        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Product with 1 Recipe",
                "fixed_costs": "10.0",
                "recipes": [{"recipe_id": recipe1_id, "quantity": "1.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        # Verify it has 1 recipe
        get_response = await client.get(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert len(get_response.json()["recipes"]) == 1

        # Create second recipe
        recipe2_id = await self.create_recipe(client, token, "Recipe 2")

        # Update product to add second recipe
        update_response = await client.put(
            f"/api/products/{product_id}",
            json={
                "name": "Product with 1 Recipe",
                "fixed_costs": "10.0",
                "recipes": [
                    {"recipe_id": recipe1_id, "quantity": "1.0"},
                    {"recipe_id": recipe2_id, "quantity": "2.0"},
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert len(updated_data["recipes"]) == 2

        # Verify persistence by fetching again
        final_response = await client.get(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        final_data = final_response.json()
        assert len(final_data["recipes"]) == 2

        # Verify recipe IDs
        recipe_ids = [r["recipe_id"] for r in final_data["recipes"]]
        assert recipe1_id in recipe_ids
        assert recipe2_id in recipe_ids

    async def test_update_product_change_recipe_quantity(self, client: AsyncClient, db_session: AsyncSession):
        """Test changing recipe quantities - verifies bug fix."""
        token = await create_admin_and_get_token(client, db_session)
        recipe_id = await self.create_recipe(client, token)

        # Create product
        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Product with Recipe",
                "fixed_costs": "8.0",
                "recipes": [{"recipe_id": recipe_id, "quantity": "1.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        # Update quantity
        update_response = await client.put(
            f"/api/products/{product_id}",
            json={
                "name": "Product with Recipe",
                "fixed_costs": "8.0",
                "recipes": [{"recipe_id": recipe_id, "quantity": "5.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert update_response.status_code == 200

        # Verify quantity was persisted
        get_response = await client.get(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = get_response.json()
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["quantity"] == "5.0"

    async def test_update_product_remove_recipes(self, client: AsyncClient, db_session: AsyncSession):
        """Test removing recipes from a product."""
        token = await create_admin_and_get_token(client, db_session)
        recipe1_id = await self.create_recipe(client, token, "Recipe 1")
        recipe2_id = await self.create_recipe(client, token, "Recipe 2")

        # Create product with two recipes
        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Product with 2 Recipes",
                "fixed_costs": "15.0",
                "recipes": [
                    {"recipe_id": recipe1_id, "quantity": "1.0"},
                    {"recipe_id": recipe2_id, "quantity": "2.0"},
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        # Update to keep only one recipe
        update_response = await client.put(
            f"/api/products/{product_id}",
            json={
                "name": "Product with 2 Recipes",
                "fixed_costs": "15.0",
                "recipes": [{"recipe_id": recipe1_id, "quantity": "1.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert update_response.status_code == 200

        # Verify only one recipe remains
        get_response = await client.get(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = get_response.json()
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["recipe_id"] == recipe1_id

    async def test_delete_product(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting a product."""
        token = await create_admin_and_get_token(client, db_session)
        recipe_id = await self.create_recipe(client, token)

        create_response = await client.post(
            "/api/products/",
            json={
                "name": "To Delete",
                "fixed_costs": "1.0",
                "recipes": [{"recipe_id": recipe_id, "quantity": "1.0"}],
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
