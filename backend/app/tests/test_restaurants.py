import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.restaurant import Restaurant

SQLALCHEMY_TEST_URL = "sqlite:///./test_restaurants.db"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    db.add_all(
        [
            Restaurant(
                name="Sakura Tokyo", cuisine="japonaise", city="Paris", price_range=3, rating=4.8
            ),
            Restaurant(
                name="Le Petit Bistrot",
                cuisine="française",
                city="Paris",
                price_range=2,
                rating=4.5,
            ),
            Restaurant(
                name="Bella Napoli", cuisine="italienne", city="Lyon", price_range=2, rating=4.2
            ),
            Restaurant(
                name="Dragon Palace", cuisine="chinoise", city="Paris", price_range=1, rating=3.7
            ),
            Restaurant(
                name="Tacos del Sur",
                cuisine="mexicaine",
                city="Bordeaux",
                price_range=1,
                rating=3.9,
            ),
            Restaurant(
                name="Le Grand Luxe", cuisine="française", city="Paris", price_range=4, rating=4.9
            ),
            Restaurant(
                name="Bouchon Lyonnais", cuisine="française", city="Lyon", price_range=2, rating=4.6
            ),
        ]
    )
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


# ── Test 1 : pagination ───────────────────────────────────────────────────────
def test_list_restaurants_pagination(client):
    response = client.get("/api/v1/restaurants?page=1&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert len(data["items"]) <= 3
    assert data["total"] == 7


# ── Test 2 : filtre cuisine ───────────────────────────────────────────────────
def test_filter_by_cuisine(client):
    response = client.get("/api/v1/restaurants?cuisine=française")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    for item in data["items"]:
        assert item["cuisine"].lower() == "française"


# ── Test 3 : filtre prix ──────────────────────────────────────────────────────
def test_filter_by_price_range(client):
    response = client.get("/api/v1/restaurants?min_price=1&max_price=2")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert 1 <= item["price_range"] <= 2


# ── Test 4 : détail par ID ────────────────────────────────────────────────────
def test_get_restaurant_by_id(client):
    response = client.get("/api/v1/restaurants/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "city" in data


# ── Test 5 : ID inexistant ────────────────────────────────────────────────────
def test_get_nonexistent_restaurant(client):
    response = client.get("/api/v1/restaurants/9999")
    assert response.status_code == 404
