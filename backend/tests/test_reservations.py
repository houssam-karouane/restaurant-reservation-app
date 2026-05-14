"""Tests d'intégration de l'API `/reservations`.

Couvre :
- création réussie / 401 / 422 / 409 (créneau pris) / restaurant inconnu
- listing `me` filtré + statut invalide
- détail accessible au propriétaire / 403 / 404
- annulation `success` / `400 H-2` / `403 not owner` / `404 not found`
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

FUTURE_DATE = (date.today() + timedelta(days=10)).isoformat()


# ─── POST /reservations ──────────────────────────────────────────────────────


def test_create_reservation_success(test_client, test_restaurant, auth_headers):
    response = test_client.post(
        "/api/v1/reservations",
        json={
            "restaurant_id": test_restaurant.id,
            "date": FUTURE_DATE,
            "time": "19:30:00",
            "number_of_people": 2,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["restaurant_id"] == test_restaurant.id
    assert body["number_of_people"] == 2
    assert body["status"] == "confirmed"


def test_create_reservation_requires_auth(test_client, test_restaurant):
    response = test_client.post(
        "/api/v1/reservations",
        json={
            "restaurant_id": test_restaurant.id,
            "date": FUTURE_DATE,
            "time": "19:30:00",
            "number_of_people": 2,
        },
    )
    assert response.status_code == 401


def test_create_reservation_rejects_zero_people(test_client, test_restaurant, auth_headers):
    response = test_client.post(
        "/api/v1/reservations",
        json={
            "restaurant_id": test_restaurant.id,
            "date": FUTURE_DATE,
            "time": "19:30:00",
            "number_of_people": 0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_reservation_rejects_too_many_people(test_client, test_restaurant, auth_headers):
    response = test_client.post(
        "/api/v1/reservations",
        json={
            "restaurant_id": test_restaurant.id,
            "date": FUTURE_DATE,
            "time": "19:30:00",
            "number_of_people": 21,
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_reservation_slot_already_taken(test_client, test_restaurant, auth_headers):
    payload = {
        "restaurant_id": test_restaurant.id,
        "date": FUTURE_DATE,
        "time": "20:00:00",
        "number_of_people": 2,
    }
    first = test_client.post("/api/v1/reservations", json=payload, headers=auth_headers)
    assert first.status_code == 201

    duplicate = test_client.post(
        "/api/v1/reservations",
        json={**payload, "number_of_people": 4},
        headers=auth_headers,
    )
    assert duplicate.status_code == 409
    assert "disponible" in duplicate.json()["detail"].lower()


# ─── GET /reservations/me ────────────────────────────────────────────────────


def test_list_me_returns_only_my_reservations(
    test_client,
    test_restaurant,
    test_user,
    other_user,
    test_db,
    auth_headers,
    make_reservation,
):
    from app.models.reservation import Reservation

    make_reservation(date=date.today() + timedelta(days=3), time=time(19, 0))

    other = Reservation(
        user_id=other_user.id,
        restaurant_id=test_restaurant.id,
        date=date.today() + timedelta(days=4),
        time=time(20, 0),
        number_of_people=2,
        status="confirmed",
    )
    test_db.add(other)
    test_db.commit()

    response = test_client.get("/api/v1/reservations/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert all(item["user_id"] == test_user.id for item in body["items"])


def test_list_me_requires_auth(test_client):
    response = test_client.get("/api/v1/reservations/me")
    assert response.status_code == 401


def test_list_me_invalid_status_filter(test_client, auth_headers):
    response = test_client.get("/api/v1/reservations/me?status=garbage", headers=auth_headers)
    assert response.status_code == 400
    assert "statut" in response.json()["detail"].lower()


def test_list_me_filter_by_status(test_client, make_reservation, auth_headers):
    make_reservation(time=time(18, 0), status="confirmed")
    make_reservation(time=time(19, 0), status="cancelled")

    response = test_client.get("/api/v1/reservations/me?status=confirmed", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "confirmed"


# ─── GET /reservations/{id} ──────────────────────────────────────────────────


def test_get_reservation_by_owner(test_client, make_reservation, auth_headers):
    reservation = make_reservation()
    response = test_client.get(f"/api/v1/reservations/{reservation.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == reservation.id


def test_get_reservation_other_user_forbidden(test_client, make_reservation, other_auth_headers):
    reservation = make_reservation()
    response = test_client.get(f"/api/v1/reservations/{reservation.id}", headers=other_auth_headers)
    assert response.status_code == 403


def test_get_reservation_not_found(test_client, auth_headers):
    response = test_client.get("/api/v1/reservations/9999", headers=auth_headers)
    assert response.status_code == 404


# ─── DELETE /reservations/{id} ───────────────────────────────────────────────


def test_cancel_reservation_success(test_client, make_reservation, auth_headers):
    reservation = make_reservation(date=date.today() + timedelta(days=7))
    response = test_client.delete(f"/api/v1/reservations/{reservation.id}", headers=auth_headers)
    assert response.status_code == 200
    assert "annulée" in response.json()["message"].lower()


def test_cancel_reservation_too_late_h_minus_2(test_client, make_reservation, auth_headers):
    """Annulation à moins de H-2 → 400."""
    soon = datetime.now() + timedelta(hours=1)
    reservation = make_reservation(date=soon.date(), time=soon.time().replace(microsecond=0))

    response = test_client.delete(f"/api/v1/reservations/{reservation.id}", headers=auth_headers)
    assert response.status_code == 400
    assert "2 heures" in response.json()["detail"]


def test_cancel_reservation_other_user_forbidden(test_client, make_reservation, other_auth_headers):
    reservation = make_reservation()
    response = test_client.delete(
        f"/api/v1/reservations/{reservation.id}", headers=other_auth_headers
    )
    assert response.status_code == 403


def test_cancel_reservation_not_found(test_client, auth_headers):
    response = test_client.delete("/api/v1/reservations/9999", headers=auth_headers)
    assert response.status_code == 404
