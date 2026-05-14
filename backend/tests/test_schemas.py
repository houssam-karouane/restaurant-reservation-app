"""Tests de validation des schémas Pydantic.

On vérifie surtout les contraintes documentées :
- ``RestaurantBase`` : ``price_range`` 1..4, ``rating`` 0..5
- ``ReservationCreate`` : ``number_of_people`` 1..20, types ``date``/``time``
- ``UserCreate`` : email validé, password requis
"""

from __future__ import annotations

from datetime import date, time

import pytest
from pydantic import ValidationError

from app.schemas.reservation import ReservationCreate
from app.schemas.restaurant import (
    RestaurantBase,
    RestaurantCreate,
    RestaurantUpdate,
)
from app.schemas.user import UserCreate


# ─── RestaurantBase / RestaurantCreate ───────────────────────────────────────


def test_restaurant_minimal_payload():
    payload = RestaurantCreate(name="Mini", cuisine="française")
    assert payload.name == "Mini"
    assert payload.price_range is None
    assert payload.rating is None


def test_restaurant_full_payload():
    payload = RestaurantBase(
        name="Full",
        cuisine="japonaise",
        city="Paris",
        address="rue X",
        price_range=4,
        rating=4.7,
        image_url="https://cdn.example.com/p.jpg",
    )
    assert payload.price_range == 4
    assert payload.rating == 4.7
    assert payload.image_url.startswith("https://")


@pytest.mark.parametrize("price", [0, 5, -1, 10])
def test_restaurant_price_range_out_of_bounds(price):
    with pytest.raises(ValidationError):
        RestaurantBase(name="X", cuisine="y", price_range=price)


@pytest.mark.parametrize("rating", [-0.1, 5.1, 10])
def test_restaurant_rating_out_of_bounds(rating):
    with pytest.raises(ValidationError):
        RestaurantBase(name="X", cuisine="y", rating=rating)


def test_restaurant_update_accepts_partial_fields():
    upd = RestaurantUpdate(name="Renamed")
    assert upd.name == "Renamed"
    assert upd.cuisine is None
    # ``exclude_unset`` doit ne contenir que le champ explicitement fourni
    assert upd.model_dump(exclude_unset=True) == {"name": "Renamed"}


# ─── ReservationCreate ───────────────────────────────────────────────────────


def test_reservation_create_valid():
    r = ReservationCreate(
        restaurant_id=1,
        date=date(2026, 12, 1),
        time=time(19, 30),
        number_of_people=2,
    )
    assert r.number_of_people == 2


@pytest.mark.parametrize("count", [0, -1, 21, 50])
def test_reservation_number_of_people_out_of_bounds(count):
    with pytest.raises(ValidationError):
        ReservationCreate(
            restaurant_id=1,
            date=date(2026, 12, 1),
            time=time(19, 30),
            number_of_people=count,
        )


def test_reservation_create_rejects_bad_date():
    with pytest.raises(ValidationError):
        ReservationCreate(
            restaurant_id=1,
            date="pas-une-date",  # type: ignore[arg-type]
            time=time(19, 30),
            number_of_people=2,
        )


def test_reservation_create_rejects_bad_time():
    with pytest.raises(ValidationError):
        ReservationCreate(
            restaurant_id=1,
            date=date(2026, 12, 1),
            time="midi",  # type: ignore[arg-type]
            number_of_people=2,
        )


# ─── UserCreate ──────────────────────────────────────────────────────────────


def test_user_create_valid():
    u = UserCreate(
        email="ok@example.com",
        username="ok",
        full_name="OK",
        password="mypassword",
    )
    assert u.email == "ok@example.com"


@pytest.mark.parametrize("bad_email", ["nope", "missing-at.com", "@invalid", "a@b"])
def test_user_create_rejects_bad_email(bad_email):
    with pytest.raises(ValidationError):
        UserCreate(email=bad_email, username="x", password="pw12345")
