"""
Basic API tests
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root health check"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_endpoint():
    """Test detailed health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "endpoints" in data


def test_score_endpoint():
    """Test scoring endpoint with sample text"""
    response = client.post(
        "/api/v1/score",
        json={
            "text": "This is a sample text for testing. It contains multiple sentences. Maybe we can analyze it?",
            "options": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "humanscore" in data
    assert "breakdown" in data
    assert "metadata" in data
    assert 0.0 <= data["humanscore"] <= 1.0


def test_score_endpoint_short_text():
    """Test scoring endpoint with too short text"""
    response = client.post(
        "/api/v1/score",
        json={
            "text": "Short",
            "options": {}
        }
    )
    # Should fail validation
    assert response.status_code == 422

