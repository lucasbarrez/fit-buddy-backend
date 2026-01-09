"""
Pytest configuration and fixtures
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def test_client() -> Generator:
    """Create a test client"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def override_get_db() -> None:
    """Override database dependency for testing"""
    # Add your test database setup here
    pass
