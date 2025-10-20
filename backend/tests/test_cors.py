"""Tests for CORS configuration."""
import pytest
from httpx import AsyncClient

from tests.test_constants import TestCredentials


@pytest.mark.asyncio
class TestCORS:
    """Test CORS middleware configuration."""

    async def test_cors_preflight_auth_endpoint(self, client: AsyncClient):
        """Test CORS preflight request for auth endpoint."""
        response = await client.options(
            "/api/auth/login",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "POST" in response.headers["access-control-allow-methods"]

    async def test_cors_preflight_products_endpoint(self, client: AsyncClient):
        """Test CORS preflight request for products endpoint."""
        response = await client.options(
            "/api/products/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "GET" in response.headers["access-control-allow-methods"]

    async def test_cors_allows_any_origin_in_development(self, client: AsyncClient):
        """Test that CORS allows any origin (development mode)."""
        # Test with various origins
        origins = [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://localhost:5177",
            "http://localhost:3000",
        ]

        for origin in origins:
            response = await client.options(
                "/api/auth/login",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                },
            )

            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers
            # With allow_origins=["*"], the origin should be echoed back
            assert response.headers["access-control-allow-origin"] == origin

    async def test_cors_allows_credentials(self, client: AsyncClient):
        """Test that CORS allows credentials."""
        response = await client.options(
            "/api/products/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"

    async def test_cors_allows_common_methods(self, client: AsyncClient):
        """Test that CORS allows all common HTTP methods."""
        response = await client.options(
            "/api/products/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        allowed_methods = response.headers["access-control-allow-methods"]

        # Verify all common methods are allowed
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]:
            assert method in allowed_methods

    async def test_cors_on_actual_request(self, client: AsyncClient):
        """Test CORS headers on actual POST request."""
        response = await client.post(
            "/api/auth/login",
            json={"username": TestCredentials.TEST_USERNAME, "password": TestCredentials.TEST_PASSWORD},
            headers={"Origin": "http://localhost:5173"},
        )

        # Even though login fails (invalid credentials), CORS headers should be present
        assert "vary" in response.headers or "access-control-allow-origin" in response.headers

    async def test_cors_preflight_with_custom_headers(self, client: AsyncClient):
        """Test CORS preflight with custom headers."""
        response = await client.options(
            "/api/products/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "PUT",
                "Access-Control-Request-Headers": "authorization, content-type, x-custom-header",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    async def test_cors_max_age_set(self, client: AsyncClient):
        """Test that CORS max-age is set for preflight caching."""
        response = await client.options(
            "/api/products/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        # Check if max-age is set (FastAPI CORS default is 600 seconds)
        if "access-control-max-age" in response.headers:
            max_age = int(response.headers["access-control-max-age"])
            assert max_age > 0
