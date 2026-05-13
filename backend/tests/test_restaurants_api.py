"""Tests d'intégration des endpoints `/restaurants`."""

from __future__ import annotations

import pytest

from app.models.restaurant import Restaurant


@pytest.fixture()
def seven_restaurants(test_db):
    """Population variée pour tester pagination, tri et filtres."""
    rows = [
        Restaurant(name="Alpha", cuisine="française", city="Paris", price_range=1, rating=3.0),
        Restaurant(name="Bravo", cuisine="japonaise", city="Paris", price_range=3, rating=4.8),
        Restaurant(name="Charlie", cuisine="italienne", city="Lyon", price_range=2, rating=4.5),
        Restaurant(name="Delta", cuisine="française", city="Lyon", price_range=4, rating=4.9),
        Restaurant(name="Echo", cuisine="japonaise", city="Marseille", price_range=2, rating=4.1),
        Restaurant(name="Foxtrot", cuisine="italienne", city="Nice", price_range=3, rating=3.5),
        Restaurant(name="Golf", cuisine="française", city="Nice", price_range=2, rating=4.6),
    ]
    test_db.add_all(rows)
    test_db.commit()
    return rows


# ─── GET /restaurants ────────────────────────────────────────────────────────


def test_list_returns_pagination_metadata(test_client, seven_restaurants):
    response = test_client.get("/api/v1/restaurants?limit=3")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 7
    assert body["page"] == 1
    assert body["pages"] == 3
    assert len(body["items"]) == 3


def test_list_sorted_by_rating_desc(test_client, seven_restaurants):
    response = test_client.get("/api/v1/restaurants?limit=50")
    items = response.json()["items"]
    ratings = [r["rating"] for r in items]
    assert ratings == sorted(ratings, reverse=True)


def test_list_filter_by_city_case_insensitive(test_client, seven_restaurants):
    response = test_client.get("/api/v1/restaurants?city=lyon")
    body = response.json()
    assert body["total"] == 2
    assert all(r["city"] == "Lyon" for r in body["items"])


def test_list_filter_by_cuisine(test_client, seven_restaurants):
    response = test_client.get("/api/v1/restaurants?cuisine=japonaise")
    body = response.json()
    assert body["total"] == 2
    assert {r["name"] for r in body["items"]} == {"Bravo", "Echo"}


def test_list_filter_by_min_rating(test_client, seven_restaurants):
    response = test_client.get("/api/v1/restaurants?min_rating=4.5")
    body = response.json()
    assert body["total"] == 4
    assert all(r["rating"] >= 4.5 for r in body["items"])


def test_list_filter_by_price_range(test_client, seven_restaurants):
    response = test_client.get("/api/v1/restaurants?min_price=2&max_price=3")
    body = response.json()
    for r in body["items"]:
        assert 2 <= r["price_range"] <= 3


def test_list_rejects_out_of_range_price(test_client):
    response = test_client.get("/api/v1/restaurants?min_price=5")
    assert response.status_code == 422


def test_list_empty_when_no_match(test_client, seven_restaurants):
    response = test_client.get("/api/v1/restaurants?city=Toulouse")
    body = response.json()
    assert body["total"] == 0
    assert body["pages"] == 1
    assert body["items"] == []


# ─── GET /restaurants/{id} ───────────────────────────────────────────────────


def test_get_restaurant_by_id(test_client, test_restaurant):
    response = test_client.get(f"/api/v1/restaurants/{test_restaurant.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == test_restaurant.id
    assert body["name"] == test_restaurant.name
    assert body["image_url"] == "https://example.com/photo.jpg"


def test_get_restaurant_not_found(test_client):
    response = test_client.get("/api/v1/restaurants/99999")
    assert response.status_code == 404
    assert "introuvable" in response.json()["detail"].lower()


# ─── POST/PUT/DELETE (admin only) ────────────────────────────────────────────


def test_create_restaurant_requires_admin(test_client, auth_headers):
    response = test_client.post(
        "/api/v1/restaurants",
        json={"name": "Banned", "cuisine": "française"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_create_restaurant_unauthenticated(test_client):
    response = test_client.post(
        "/api/v1/restaurants",
        json={"name": "Banned", "cuisine": "française"},
    )
    assert response.status_code == 401


def test_update_restaurant_requires_admin(test_client, test_restaurant, auth_headers):
    response = test_client.put(
        f"/api/v1/restaurants/{test_restaurant.id}",
        json={"name": "Renamed"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_restaurant_requires_admin(test_client, test_restaurant, auth_headers):
    response = test_client.delete(
        f"/api/v1/restaurants/{test_restaurant.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403
