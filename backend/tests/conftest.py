"""
Configuration Pytest pour les tests backend.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Client de test pour FastAPI."""
    return TestClient(app)
