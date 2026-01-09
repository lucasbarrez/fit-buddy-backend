"""
Tests for health endpoints
"""

from fastapi.testclient import TestClient


def test_health_check(test_client: TestClient) -> None:
    """Test health check endpoint"""
    response = test_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "services" in data


def test_root_endpoint(test_client: TestClient) -> None:
    """Test root endpoint"""
    response = test_client.get("/api/v1/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
