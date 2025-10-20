"""Tests for API routes validation and error handling."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from tests.test_helpers import create_admin_and_get_token, create_test_user, get_auth_token
from src.domain.value_objects.user_role import UserRole


@pytest.mark.asyncio
class TestRoutesValidation:
    """Test API routes validation and edge cases."""

    async def test_create_ingredient_missing_fields(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating ingredient with missing fields."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/ingredients/",
            json={"name": "Test"},  # Missing unit
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    async def test_update_ingredient_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating non-existent ingredient."""
        from uuid import uuid4
        token = await create_admin_and_get_token(client, db_session)

        response = await client.put(
            f"/api/ingredients/{uuid4()}",
            json={"name": "Updated", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_delete_ingredient_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting non-existent ingredient."""
        from uuid import uuid4
        token = await create_admin_and_get_token(client, db_session)

        response = await client.delete(
            f"/api/ingredients/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_get_ingredient_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting ingredient by ID."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        create_response = await client.post(
            "/api/ingredients/",
            json={"name": "Test Ingredient Get", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = create_response.json()["id"]

        # Get ingredient
        response = await client.get(
            f"/api/ingredients/{ingredient_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ingredient_id
        assert data["name"] == "Test Ingredient Get"

    async def test_update_ingredient_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating ingredient successfully."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        create_response = await client.post(
            "/api/ingredients/",
            json={"name": "Original Name", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = create_response.json()["id"]

        # Update ingredient
        response = await client.put(
            f"/api/ingredients/{ingredient_id}",
            json={"name": "Updated Name", "unit": "g"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["unit"] == "g"

    async def test_create_recipe_empty_name(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating recipe with empty name."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/recipes/",
            json={"name": "", "instructions": "Test", "ingredients": []},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    async def test_get_recipe_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting recipe by ID."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient first
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Recipe Test Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        create_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Test Recipe Get",
                "instructions": "Mix well",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = create_response.json()["id"]

        # Get recipe
        response = await client.get(
            f"/api/recipes/{recipe_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recipe_id
        assert data["name"] == "Test Recipe Get"
        assert len(data["ingredients"]) == 1

    async def test_update_recipe_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating recipe successfully."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Update Recipe Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        create_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Original Recipe",
                "instructions": "Original",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = create_response.json()["id"]

        # Update recipe
        response = await client.put(
            f"/api/recipes/{recipe_id}",
            json={
                "name": "Updated Recipe",
                "instructions": "Updated instructions",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.8}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Recipe"
        assert data["instructions"] == "Updated instructions"

    async def test_delete_recipe_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting recipe successfully."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Delete Recipe Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        create_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Recipe to Delete",
                "instructions": "Delete me",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = create_response.json()["id"]

        # Delete recipe
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

    async def test_create_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating product successfully."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Product Test Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Product Recipe",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = recipe_response.json()["id"]

        # Create product
        response = await client.post(
            "/api/products/",
            json={
                "name": "Test Product",
                "price": 10.99,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert len(data["recipes"]) == 1

    async def test_get_product_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting product by ID."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient and recipe
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Get Product Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Get Product Recipe",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = recipe_response.json()["id"]

        # Create product
        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Get Test Product",
                "price": 15.99,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        # Get product
        response = await client.get(
            f"/api/products/{product_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Get Test Product"

    async def test_update_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating product successfully."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient and recipe
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Update Product Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Update Product Recipe",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = recipe_response.json()["id"]

        # Create product
        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Original Product",
                "price": 10.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        # Update product
        response = await client.put(
            f"/api/products/{product_id}",
            json={
                "name": "Updated Product",
                "price": 15.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 2.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"

    async def test_delete_product_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting product successfully."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient and recipe
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Delete Product Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Delete Product Recipe",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = recipe_response.json()["id"]

        # Create product
        create_response = await client.post(
            "/api/products/",
            json={
                "name": "Product to Delete",
                "price": 10.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = create_response.json()["id"]

        # Delete product
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

    async def test_order_status_update_invalid_status(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating order with invalid status."""
        token = await create_admin_and_get_token(client, db_session)

        # Create product first
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": "Order Status Flour", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": "Order Status Recipe",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = recipe_response.json()["id"]

        product_response = await client.post(
            "/api/products/",
            json={
                "name": "Order Status Product",
                "price": 10.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        product_id = product_response.json()["id"]

        # Create order
        order_response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "Test Customer",
                "customer_email": "status@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        order_id = order_response.json()["id"]

        # Try to update with invalid status
        response = await client.patch(
            f"/api/orders/{order_id}/status",
            json={"status": "invalid_status"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422
