import pytest
from datetime import date, time, datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.reservation import Reservation
from app.models.restaurant import Restaurant
from app.models.user import User
from app.core.security import create_access_token

SQLALCHEMY_TEST_URL = "sqlite:///./test_reservations.db"
engine_test = create_engine(SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()

    # Créer un user de test
    user = User(
        id=1, email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        is_active=True,
    )
    other_user = User(
        id=2, email="other@example.com",
        username="otheruser",
        hashed_password="hashed",
        is_active=True,
    )
    restaurant = Restaurant(
        id=1, name="Test Restaurant",
        cuisine="française", city="Paris",
        price_range=2, rating=4.5,
    )
    db.add_all([user, other_user, restaurant])
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
def auth_headers():
    """Headers JWT pour l'utilisateur de test."""
    token = create_access_token(subject="test@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers():
    """Headers JWT pour un autre utilisateur."""
    token = create_access_token(subject="other@example.com")
    return {"Authorization": f"Bearer {token}"}


# ── Test 1 : créer une réservation ───────────────────────────────────────────

def test_create_reservation_success(client, auth_headers):
    """POST /reservations → 201 avec un créneau libre."""
    future_date = (datetime.now() + timedelta(days=5)).date()

    response = client.post("/api/v1/reservations", json={
        "restaurant_id": 1,
        "date": str(future_date),
        "time": "19:30:00",
        "number_of_people": 2,
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["restaurant_id"] == 1
    assert data["number_of_people"] == 2
    assert data["status"] == "confirmed"


# ── Test 2 : créneau indisponible ─────────────────────────────────────────────

def test_create_reservation_unavailable_slot(client, auth_headers):
    """POST /reservations → 409 si créneau déjà pris."""
    future_date = (datetime.now() + timedelta(days=10)).date()

    # Première réservation
    client.post("/api/v1/reservations", json={
        "restaurant_id": 1,
        "date": str(future_date),
        "time": "20:00:00",
        "number_of_people": 2,
    }, headers=auth_headers)

    # Deuxième réservation sur le même créneau → 409
    response = client.post("/api/v1/reservations", json={
        "restaurant_id": 1,
        "date": str(future_date),
        "time": "20:00:00",
        "number_of_people": 4,
    }, headers=auth_headers)

    assert response.status_code == 409
    assert "disponible" in response.json()["detail"].lower()


# ── Test 3 : lister mes réservations ─────────────────────────────────────────

def test_list_my_reservations(client, auth_headers):
    """GET /reservations/me → 200 avec la liste des réservations du user."""
    response = client.get("/api/v1/reservations/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    # Toutes les réservations appartiennent au user courant
    for item in data["items"]:
        assert item["user_id"] == 1


# ── Test 4 : annuler une réservation ─────────────────────────────────────────

def test_cancel_reservation_success(client, auth_headers):
    """DELETE /reservations/{id} → 200 si dans les délais."""
    # Créer une réservation dans 5 jours (bien avant H-2)
    future_date = (datetime.now() + timedelta(days=5)).date()
    create_response = client.post("/api/v1/reservations", json={
        "restaurant_id": 1,
        "date": str(future_date),
        "time": "21:00:00",
        "number_of_people": 2,
    }, headers=auth_headers)
    reservation_id = create_response.json()["id"]

    # Annuler
    response = client.delete(
        f"/api/v1/reservations/{reservation_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "annulée" in response.json()["message"].lower()


# ── Test 5 : annulation trop tard (H-2) ──────────────────────────────────────

def test_cancel_reservation_too_late(client, db_session, auth_headers):
    """DELETE /reservations/{id} → 400 si moins de 2h avant."""
    # Créer une réservation dans 1h (trop tard pour annuler)
    soon = datetime.now() + timedelta(hours=1)
    reservation = Reservation(
        id=99,
        user_id=1,
        restaurant_id=1,
        date=soon.date(),
        time=soon.time(),
        number_of_people=2,
        status="confirmed",
    )
    db_session.add(reservation)
    db_session.commit()

    response = client.delete("/api/v1/reservations/99", headers=auth_headers)
    assert response.status_code == 400
    assert "2 heures" in response.json()["detail"]


# ── Test 6 : annuler la réservation d'un autre user ──────────────────────────

def test_cancel_other_user_reservation_forbidden(client, auth_headers, other_auth_headers):
    """DELETE /reservations/{id} → 403 si pas le propriétaire."""
    # Créer une réservation avec other_user
    future_date = (datetime.now() + timedelta(days=7)).date()
    create_response = client.post("/api/v1/reservations", json={
        "restaurant_id": 1,
        "date": str(future_date),
        "time": "18:00:00",
        "number_of_people": 3,
    }, headers=other_auth_headers)
    reservation_id = create_response.json()["id"]

    # Tenter d'annuler avec le premier user → 403
    response = client.delete(
        f"/api/v1/reservations/{reservation_id}",
        headers=auth_headers
    )
    assert response.status_code == 403
    assert "autre utilisateur" in response.json()["detail"].lower()