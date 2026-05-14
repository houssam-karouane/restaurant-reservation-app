import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, time
from app.main import app
from app.database import Base, get_db
from app.models.restaurant import Restaurant
from app.models.reservation import Reservation
from app.models.user import User
from app.core.security import create_access_token

SQLALCHEMY_TEST_URL = "sqlite:///./test_reviews.db"
engine_test = create_engine(
    SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()

    # 1. Création des utilisateurs
    user_valid = User(
        id=20,
        email="valid@test.com",
        username="valid",
        hashed_password="pw",
        is_active=True,
    )
    user_invalid = User(
        id=21,
        email="invalid@test.com",
        username="invalid",
        hashed_password="pw",
        is_active=True,
    )
    db.add_all([user_valid, user_invalid])

    # 2. Création d'un restaurant (Note initiale : 0.0)
    restaurant = Restaurant(
        id=20,
        name="Le Testeur",
        cuisine="française",
        city="Paris",
        price_range=2,
        rating=0.0,
    )
    db.add(restaurant)
    db.commit()

    # 3. Création d'une réservation "completed" uniquement pour user_valid
    # 3. Création d'une réservation "completed" uniquement pour user_valid
    reservation = Reservation(
        id=20,
        user_id=20,
        restaurant_id=20,
        status="completed",
        number_of_people=2,
        date=date(2026, 5, 14),  # <-- Ajout obligatoire
        time=time(19, 0),  # <-- Ajout obligatoire
    )
    db.add(reservation)
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
def headers_valid():
    return {"Authorization": f"Bearer {create_access_token(subject='valid@test.com')}"}


@pytest.fixture
def headers_invalid():
    return {
        "Authorization": f"Bearer {create_access_token(subject='invalid@test.com')}"
    }


# ─── TESTS ─────


def test_create_review_forbidden(client, headers_invalid):
    """Test : Un utilisateur sans réservation terminée doit recevoir une erreur 403."""
    payload = {"restaurant_id": 20, "rating": 5, "comment": "Super !"}
    response = client.post("/api/v1/reviews/", headers=headers_invalid, json=payload)

    assert response.status_code == 403
    assert "réservation terminée" in response.json()["detail"]


def test_create_review_success_and_rating_update(client, headers_valid, db_session):
    """Test : Création réussie + vérification du recalcul de la moyenne."""
    # 1. Création du premier avis (Note 4)
    payload1 = {"restaurant_id": 20, "rating": 4, "comment": "Très bien"}
    resp1 = client.post("/api/v1/reviews/", headers=headers_valid, json=payload1)

    assert resp1.status_code == 200
    assert resp1.json()["rating"] == 4

    # Vérification du Side Effect (Le restaurant doit avoir 4.0)
    restaurant = db_session.query(Restaurant).filter(Restaurant.id == 20).first()
    assert restaurant.rating == 4.0

    # 2. Création d'un deuxième avis par le même user (Note 5)
    payload2 = {"restaurant_id": 20, "rating": 5, "comment": "Parfait"}
    client.post("/api/v1/reviews/", headers=headers_valid, json=payload2)

    # Vérification du Side Effect (La moyenne de 4 et 5 doit faire 4.5)
    db_session.refresh(restaurant)
    assert restaurant.rating == 4.5


def test_get_restaurant_reviews(client):
    """Test : Récupération de la liste des avis publics."""
    response = client.get("/api/v1/reviews/restaurant/20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Car on a créé 2 avis juste au-dessus
    assert data[0]["rating"] == 4
