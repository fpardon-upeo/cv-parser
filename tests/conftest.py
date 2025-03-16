import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import Settings, settings
from app.main import app  # This will be created later


@pytest.fixture
def test_settings() -> Settings:
    """Fixture for test settings."""
    return settings


@pytest.fixture
def client() -> TestClient:
    """Fixture for FastAPI test client."""
    return TestClient(app) 