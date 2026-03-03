"""Tests for custom HTTP routes using pytest framework."""

import json

import pytest
from starlette.testclient import TestClient


class TestHealthCheckRoute:
    """Test cases for the /health custom route."""

    def test_health_route_is_registered(self):
        """Test that the /health route is registered in the app."""
        from src.server import app

        paths = [route.path for route in app._additional_http_routes]
        assert "/health" in paths

    def test_health_route_methods(self):
        """Test that the /health route accepts GET requests."""
        from src.server import app

        health_route = next(r for r in app._additional_http_routes if r.path == "/health")
        assert "GET" in health_route.methods

    @pytest.mark.asyncio
    async def test_health_check_returns_ok_status(self):
        """Test that the health_check function returns status ok."""
        from src.server import health_check

        response = await health_check(request=None)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check_response_body(self):
        """Test that the health_check response body contains status ok."""
        from src.server import health_check

        response = await health_check(request=None)
        body = json.loads(response.body)
        assert body == {"status": "ok"}

    def test_health_endpoint_via_http_client(self):
        """Test the /health endpoint returns 200 via HTTP test client."""
        from src.server import app

        client = TestClient(app.http_app())
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
