import pytest
import json
from datetime import date, time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.restaurant import Restaurant
from app.models.reservation import Reservation
from app.models.user import User
from app.core.security import create_access_token

SQLALCHEMY_TEST_URL = "sqlite:///./test_recommendations.db"
engine_test = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()

    # Users
    user_with_history = User(
        id=10,
        email="history@test.com",
        username="history_user",
        hashed_password="hashed",
        is_active=True,
    )
    new_user = User(
        id=11,
        email="newuser@test.com",
        username="new_user",
        hashed_password="hashed",
        is_active=True,
    )
    db.add_all([user_with_history, new_user])

    # Restaurants
    restaurants = [
        Restaurant(
            id=10, name="Sakura", cuisine="japonaise", city="Paris", price_range=3, rating=4.9
        ),
        Restaurant(
            id=11, name="Le Bistrot", cuisine="française", city="Paris", price_range=2, rating=4.7
        ),
        Restaurant(
            id=12, name="Bella Napoli", cuisine="italienne", city="Lyon", price_range=2, rating=4.6
        ),
        Restaurant(
            id=13, name="Dragon", cuisine="chinoise", city="Paris", price_range=1, rating=4.2
        ),
        Restaurant(
            id=14,
            name="Spice Garden",
            cuisine="indienne",
            city="Marseille",
            price_range=2,
            rating=4.8,
        ),
        Restaurant(
            id=15, name="Tacos", cuisine="mexicaine", city="Bordeaux", price_range=1, rating=3.9
        ),
        Restaurant(
            id=16, name="Luxe", cuisine="française", city="Paris", price_range=4, rating=4.5
        ),
    ]
    db.add_all(restaurants)

    # Réservations passées pour user_with_history
    # Réservations passées pour user_with_history
    # Réservations passées pour user_with_history
    reservations = [
        Reservation(
            id=10,
            user_id=10,
            restaurant_id=10,
            date=date(2026, 5, 15),
            time=time(19, 0, 0),  # <-- Vrais objets Python
            status="completed",
            number_of_people=2,
        ),
        Reservation(
            id=11,
            user_id=10,
            restaurant_id=11,
            date=date(2026, 5, 16),
            time=time(20, 0, 0),  # <-- Vrais objets Python
            status="completed",
            number_of_people=2,
        ),
    ]
    db.add_all(reservations)
    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="module")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def headers_with_history():
    token = create_access_token(subject="history@test.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def headers_new_user():
    token = create_access_token(subject="newuser@test.com")
    return {"Authorization": f"Bearer {token}"}


# ── Test 1 : user avec historique ────────────────────────────────────────────


def test_recommendations_with_history(client, headers_with_history):
    """GET /recommendations/me → 200 avec recommandations personnalisées."""
    # Désactiver le cache pour ce test
    with patch(
        "app.api.v1.endpoints.recommendations.get_cached_recommendations", return_value=None
    ), patch("app.api.v1.endpoints.recommendations.set_cached_recommendations"):

        response = client.get(
            "/api/v1/recommendations/me",
            headers=headers_with_history,
        )

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "fallback" in data
    assert "from_cache" in data

    assert data["fallback"] is False
    assert data["total"] <= 6
    assert len(data["items"]) <= 6

    # Vérifier la structure de chaque item
    for item in data["items"]:
        assert "id" in item
        assert "name" in item
        assert "score" in item
        assert "score_reason" in item
        assert "rating" in item


# ── Test 2 : nouveau user sans historique (fallback) ─────────────────────────


def test_recommendations_new_user(client, headers_new_user):
    """GET /recommendations/me → fallback=True si aucun historique."""
    with patch(
        "app.api.v1.endpoints.recommendations.get_cached_recommendations", return_value=None
    ), patch("app.api.v1.endpoints.recommendations.set_cached_recommendations"):

        response = client.get(
            "/api/v1/recommendations/me",
            headers=headers_new_user,
        )

    assert response.status_code == 200
    data = response.json()

    # Nouveau user → fallback activé
    assert data["fallback"] is True
    assert data["total"] <= 6

    # Fallback = top par rating → triés par note décroissante
    ratings = [item["rating"] for item in data["items"]]
    assert ratings == sorted(ratings, reverse=True)

    # score_reason = "top rated" pour le fallback
    for item in data["items"]:
        assert item["score_reason"] == "top rated"


# ── Test 3 : cache Redis ──────────────────────────────────────────────────────


def test_recommendations_cached(client, headers_with_history):
    """GET /recommendations/me → from_cache=True si données en cache."""
    cached_data = [
        {
            "id": 10,
            "name": "Sakura",
            "cuisine": "japonaise",
            "city": "Paris",
            "price_range": 3,
            "rating": 4.9,
            "score": 8.0,
            "score_reason": "cuisine préférée",
        }
    ]

    with patch(
        "app.api.v1.endpoints.recommendations.get_cached_recommendations", return_value=cached_data
    ):

        response = client.get(
            "/api/v1/recommendations/me",
            headers=headers_with_history,
        )

    assert response.status_code == 200
    data = response.json()

    # Doit venir du cache
    assert data["from_cache"] is True
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Sakura"
    assert data["items"][0]["score"] == 8.0
