"""
Tests de base pour vérifier que l'API démarre.
"""


def test_health_endpoint(client):
    """Test que l'endpoint /health répond."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_root_endpoint(client):
    """Test que la route racine répond."""
    response = client.get("/")
    assert response.status_code == 200
