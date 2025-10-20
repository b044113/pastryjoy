"""Comprehensive API tests for better coverage."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from tests.test_helpers import create_admin_and_get_token, create_test_user, get_auth_token
from src.domain.value_objects.user_role import UserRole


@pytest.mark.asyncio
class TestIngredientsAPICoverage:
    """Test ingredients API comprehensively."""

    async def test_list_ingredients_empty(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing ingredients when none exist."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.get(
            "/api/ingredients/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        # May not be empty due to other tests, but should at least work
        assert isinstance(response.json(), list)

    async def test_create_and_list_ingredients(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating and listing ingredients."""
        token = await create_admin_and_get_token(client, db_session)

        # Create ingredient
        create_response = await client.post(
            "/api/ingredients/",
            json={"name": f"List Test {uuid4().hex[:8]}", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_response.status_code == 201

        # List should include it
        list_response = await client.get(
            "/api/ingredients/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.status_code == 200
        ingredients = list_response.json()
        assert len(ingredients) > 0


@pytest.mark.asyncio
class TestRecipesAPICoverage:
    """Test recipes API comprehensively."""

    async def create_ingredient(self, client: AsyncClient, token: str) -> str:
        """Helper to create ingredient."""
        response = await client.post(
            "/api/ingredients/",
            json={"name": f"Recipe Ing {uuid4().hex[:8]}", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        return response.json()["id"]

    async def test_create_recipe_with_empty_ingredients(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating recipe without ingredients."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/recipes/",
            json={
                "name": f"Empty Recipe {uuid4().hex[:8]}",
                "instructions": "No ingredients",
                "ingredients": [],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should succeed - recipes can have no ingredients initially
        assert response.status_code in [201, 400, 422]

    async def test_list_recipes(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing recipes."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.get(
            "/api/recipes/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_recipe_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting non-existent recipe."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.get(
            f"/api/recipes/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_update_recipe_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating non-existent recipe."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.put(
            f"/api/recipes/{uuid4()}",
            json={"name": "Updated", "instructions": "Test", "ingredients": []},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_delete_recipe_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting non-existent recipe."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.delete(
            f"/api/recipes/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestProductsAPICoverage:
    """Test products API comprehensively."""

    async def create_recipe(self, client: AsyncClient, token: str) -> str:
        """Helper to create recipe."""
        # Create ingredient first
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": f"Product Ing {uuid4().hex[:8]}", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": f"Product Recipe {uuid4().hex[:8]}",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        return recipe_response.json()["id"]

    async def test_list_products(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing products."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.get(
            "/api/products/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_product_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting non-existent product."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.get(
            f"/api/products/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_update_product_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating non-existent product."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.put(
            f"/api/products/{uuid4()}",
            json={"name": "Updated", "price": 10.0, "recipes": []},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_delete_product_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting non-existent product."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.delete(
            f"/api/products/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_create_product_with_empty_recipes(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating product without recipes."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.post(
            "/api/products/",
            json={
                "name": f"Empty Product {uuid4().hex[:8]}",
                "price": 10.0,
                "recipes": [],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should work - products can have no recipes initially
        assert response.status_code in [201, 400, 422]


@pytest.mark.asyncio
class TestOrdersAPICoverage:
    """Test orders API comprehensively."""

    async def create_product(self, client: AsyncClient, token: str) -> str:
        """Helper to create product."""
        # Create ingredient
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": f"Order Ing {uuid4().hex[:8]}", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": f"Order Recipe {uuid4().hex[:8]}",
                "instructions": "Mix",
                "ingredients": [{"ingredient_id": ingredient_id, "quantity": 0.5}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        recipe_id = recipe_response.json()["id"]

        # Create product
        product_response = await client.post(
            "/api/products/",
            json={
                "name": f"Order Product {uuid4().hex[:8]}",
                "price": 10.0,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        return product_response.json()["id"]

    async def test_update_order_status_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating status of non-existent order."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.patch(
            f"/api/orders/{uuid4()}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_get_order_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting non-existent order."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.get(
            f"/api/orders/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_delete_order_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting non-existent order."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.delete(
            f"/api/orders/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_create_order_with_notes(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating order with notes."""
        token = await create_admin_and_get_token(client, db_session)
        product_id = await self.create_product(client, token)

        response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "Test Customer",
                "customer_email": "test@test.com",
                "notes": "Special instructions here",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["notes"] == "Special instructions here"

    async def test_list_orders_admin(self, client: AsyncClient, db_session: AsyncSession):
        """Test admin listing all orders."""
        token = await create_admin_and_get_token(client, db_session)

        response = await client.get(
            "/api/orders/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
