"""Fixtures partagées pour la suite de tests backend.

- ``test_db``        : session SQLAlchemy isolée par test (SQLite en mémoire).
- ``test_client``    : ``TestClient`` FastAPI avec ``get_db`` override.
- ``test_user``      : user persisté en base de test.
- ``other_user``     : second user pour les cas d'autorisation.
- ``test_token``     : JWT valide pour ``test_user``.
- ``auth_headers``   : header Authorization Bearer prêt à l'emploi.
- ``test_restaurant`` : restaurant persisté en base de test.
- ``make_reservation`` : factory de réservations.
"""

from __future__ import annotations

import os

# Force une URL inoffensive avant l'import de l'app : ``app.database`` lit
# DATABASE_URL au chargement, donc ce ``setenv`` doit précéder tout import.
os.environ.setdefault("DATABASE_URL", "sqlite:///./_pytest_default.db")

from datetime import date, time, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.security import create_access_token, get_password_hash  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.db import base  # noqa: E402,F401  # force-load de tous les modèles
from app.main import app  # noqa: E402
from app.models.reservation import Reservation  # noqa: E402
from app.models.restaurant import Restaurant  # noqa: E402
from app.models.user import User  # noqa: E402


# ─── Infra SQLite en mémoire ─────────────────────────────────────────────────


@pytest.fixture(scope="session")
def _engine():
    """Engine SQLite partagé pour toute la session de tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def test_db(_engine):
    """Session SQLAlchemy isolée par test (nettoyage à la fin)."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()


# ─── TestClient avec override de get_db ──────────────────────────────────────


@pytest.fixture()
def test_client(test_db):
    """``TestClient`` qui injecte ``test_db`` à la place de la session réelle."""

    def _override():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def client(test_client):
    """Alias rétro-compatible avec l'ancien fixture ``client``."""
    return test_client


# ─── Données de test ─────────────────────────────────────────────────────────


@pytest.fixture()
def test_user(test_db) -> User:
    user = User(
        email="alice@test.com",
        username="alice",
        full_name="Alice Test",
        hashed_password=get_password_hash("alicepass123"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture()
def other_user(test_db) -> User:
    user = User(
        email="bob@test.com",
        username="bob",
        full_name="Bob Test",
        hashed_password=get_password_hash("bobpass12345"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture()
def test_token(test_user) -> str:
    return create_access_token(subject=test_user.email)


@pytest.fixture()
def auth_headers(test_token) -> dict:
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture()
def other_token(other_user) -> str:
    return create_access_token(subject=other_user.email)


@pytest.fixture()
def other_auth_headers(other_token) -> dict:
    return {"Authorization": f"Bearer {other_token}"}


@pytest.fixture()
def test_restaurant(test_db) -> Restaurant:
    restaurant = Restaurant(
        name="Le Test Bistrot",
        cuisine="française",
        city="Paris",
        address="1 rue du Test",
        price_range=2,
        rating=4.5,
        review_count=10,
        image_url="https://example.com/photo.jpg",
    )
    test_db.add(restaurant)
    test_db.commit()
    test_db.refresh(restaurant)
    return restaurant


@pytest.fixture()
def make_reservation(test_db, test_user, test_restaurant):
    """Factory : crée une réservation persistée, surcharge libre via kwargs."""

    def _make(**overrides) -> Reservation:
        defaults = dict(
            user_id=test_user.id,
            restaurant_id=test_restaurant.id,
            date=date.today() + timedelta(days=5),
            time=time(19, 30),
            number_of_people=2,
            status="confirmed",
        )
        defaults.update(overrides)
        reservation = Reservation(**defaults)
        test_db.add(reservation)
        test_db.commit()
        test_db.refresh(reservation)
        return reservation

    return _make
