"""Tests for orders endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_helpers import create_test_user, get_auth_token, create_admin_and_get_token
from src.domain.value_objects.user_role import UserRole


@pytest.mark.asyncio
class TestOrders:
    """Test orders CRUD endpoints."""

    async def create_product(self, client: AsyncClient, token: str, name: str, price: float) -> int:
        """Helper to create a product."""
        # Create ingredient
        ing_response = await client.post(
            "/api/ingredients/",
            json={"name": f"Flour-{name}", "unit": "kg"},
            headers={"Authorization": f"Bearer {token}"},
        )
        ingredient_id = ing_response.json()["id"]

        # Create recipe
        recipe_response = await client.post(
            "/api/recipes/",
            json={
                "name": f"Recipe-{name}",
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
                "name": name,
                "price": price,
                "recipes": [{"recipe_id": recipe_id, "quantity": 1.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        return product_response.json()["id"]

    async def test_create_order_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating an order successfully."""
        # Admin creates products
        admin_token = await create_admin_and_get_token(client, db_session)
        product_id = await self.create_product(client, admin_token, "Bread", 5.99)

        # Regular user creates order
        await create_test_user(db_session, "user1@test.com", "user1", "pass123", UserRole.USER)
        user_token = await get_auth_token(client, "user1", "pass123")

        response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "John Doe",
                "customer_email": "john@test.com",
                "items": [{"product_id": product_id, "quantity": 2, "unit_price": "5.99"}],
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "John Doe"
        assert data["customer_email"] == "john@test.com"
        assert len(data["items"]) == 1
        assert float(data["items"][0]["quantity"]) == 2.0
        assert data["status"] == "pending"

    async def test_create_order_unauthorized(self, client: AsyncClient):
        """Test creating order without authentication."""
        response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "Test",
                "items": [],
            },
        )

        assert response.status_code == 401

    async def test_get_user_orders(self, client: AsyncClient, db_session: AsyncSession):
        """Test user can only see their own orders."""
        # Admin creates product
        admin_token = await create_admin_and_get_token(client, db_session)
        product_id = await self.create_product(client, admin_token, "Product", 10.0)

        # Create two users
        await create_test_user(db_session, "user1@test.com", "user1", "pass123", UserRole.USER)
        await create_test_user(db_session, "user2@test.com", "user2", "pass123", UserRole.USER)
        user1_token = await get_auth_token(client, "user1", "pass123")
        user2_token = await get_auth_token(client, "user2", "pass123")

        # User 1 creates order
        await client.post(
            "/api/orders/",
            json={
                "customer_name": "User 1",
                "customer_email": "user1order@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        # User 2 creates order
        await client.post(
            "/api/orders/",
            json={
                "customer_name": "User 2",
                "customer_email": "user2order@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        # User 1 should only see their order
        response1 = await client.get(
            "/api/orders/",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert response1.status_code == 200
        orders1 = response1.json()
        assert all(order["customer_name"] == "User 1" for order in orders1)

        # User 2 should only see their order
        response2 = await client.get(
            "/api/orders/",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response2.status_code == 200
        orders2 = response2.json()
        assert all(order["customer_name"] == "User 2" for order in orders2)

    async def test_get_order_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting a specific order by ID."""
        admin_token = await create_admin_and_get_token(client, db_session)
        product_id = await self.create_product(client, admin_token, "Cake", 15.0)

        await create_test_user(db_session, "user1@test.com", "user1", "pass123", UserRole.USER)
        user_token = await get_auth_token(client, "user1", "pass123")

        create_response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "Jane Doe",
                "customer_email": "jane@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "15.0"}],
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        order_id = create_response.json()["id"]

        response = await client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["customer_name"] == "Jane Doe"

    async def test_update_order_status(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating order status (admin-only functionality)."""
        admin_token = await create_admin_and_get_token(client, db_session)
        product_id = await self.create_product(client, admin_token, "Product", 10.0)

        create_response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "Test Customer",
                "customer_email": "testcustomer@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        order_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/orders/{order_id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    async def test_delete_order(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting an order (admin only)."""
        admin_token = await create_admin_and_get_token(client, db_session)
        product_id = await self.create_product(client, admin_token, "Product", 10.0)

        create_response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "To Delete",
                "customer_email": "todelete@test.com",
                "items": [{"product_id": product_id, "quantity": 1, "unit_price": "10.0"}],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        order_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert get_response.status_code == 404

    async def test_create_order_with_multiple_items(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating an order with multiple items."""
        admin_token = await create_admin_and_get_token(client, db_session)
        product1_id = await self.create_product(client, admin_token, "Bread", 5.0)
        product2_id = await self.create_product(client, admin_token, "Cake", 10.0)

        await create_test_user(db_session, "user1@test.com", "user1", "pass123", UserRole.USER)
        user_token = await get_auth_token(client, "user1", "pass123")

        response = await client.post(
            "/api/orders/",
            json={
                "customer_name": "Multi Item Customer",
                "customer_email": "multi@test.com",
                "items": [
                    {"product_id": product1_id, "quantity": 3, "unit_price": "5.0"},
                    {"product_id": product2_id, "quantity": 1, "unit_price": "10.0"},
                ],
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 2
        assert float(data["total"]) > 0
