"""Tests unitaires des règles métier dans ``app.crud.reservation``.

On exerce directement les fonctions sans passer par HTTP pour cibler
précisément ``is_slot_available`` et ``can_cancel`` (règle H-2).
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from types import SimpleNamespace

import pytest

from app.crud import reservation as crud
from app.models.reservation import Reservation

# ─── is_slot_available ───────────────────────────────────────────────────────


def test_slot_available_on_empty_db(test_db, test_restaurant):
    assert (
        crud.is_slot_available(
            db=test_db,
            restaurant_id=test_restaurant.id,
            date=date.today() + timedelta(days=2),
            time=time(20, 0),
            number_of_people=2,
        )
        is True
    )


def test_slot_taken_blocks_new_reservation(test_db, test_restaurant, test_user):
    booked = Reservation(
        user_id=test_user.id,
        restaurant_id=test_restaurant.id,
        date=date.today() + timedelta(days=2),
        time=time(20, 0),
        number_of_people=2,
        status="confirmed",
    )
    test_db.add(booked)
    test_db.commit()

    assert (
        crud.is_slot_available(
            db=test_db,
            restaurant_id=test_restaurant.id,
            date=booked.date,
            time=booked.time,
            number_of_people=4,
        )
        is False
    )


def test_cancelled_reservation_does_not_block_slot(test_db, test_restaurant, test_user):
    cancelled = Reservation(
        user_id=test_user.id,
        restaurant_id=test_restaurant.id,
        date=date.today() + timedelta(days=2),
        time=time(20, 0),
        number_of_people=2,
        status="cancelled",
    )
    test_db.add(cancelled)
    test_db.commit()

    assert (
        crud.is_slot_available(
            db=test_db,
            restaurant_id=test_restaurant.id,
            date=cancelled.date,
            time=cancelled.time,
            number_of_people=2,
        )
        is True
    )


def test_different_time_same_day_is_available(test_db, test_restaurant, test_user):
    test_db.add(
        Reservation(
            user_id=test_user.id,
            restaurant_id=test_restaurant.id,
            date=date.today() + timedelta(days=2),
            time=time(19, 0),
            number_of_people=2,
            status="confirmed",
        )
    )
    test_db.commit()
    assert (
        crud.is_slot_available(
            db=test_db,
            restaurant_id=test_restaurant.id,
            date=date.today() + timedelta(days=2),
            time=time(21, 0),
            number_of_people=2,
        )
        is True
    )


# ─── create_reservation ──────────────────────────────────────────────────────


def test_create_reservation_persists_confirmed(test_db, test_user, test_restaurant):
    res = crud.create_reservation(
        db=test_db,
        user_id=test_user.id,
        restaurant_id=test_restaurant.id,
        date=date.today() + timedelta(days=3),
        time=time(19, 0),
        number_of_people=3,
    )
    assert res.id is not None
    assert res.status == "confirmed"
    assert res.number_of_people == 3


# ─── get_user_reservations ───────────────────────────────────────────────────


def test_get_user_reservations_returns_only_owner(
    test_db, test_user, other_user, test_restaurant
):
    test_db.add_all(
        [
            Reservation(
                user_id=test_user.id,
                restaurant_id=test_restaurant.id,
                date=date.today() + timedelta(days=3),
                time=time(19, 0),
                number_of_people=2,
                status="confirmed",
            ),
            Reservation(
                user_id=other_user.id,
                restaurant_id=test_restaurant.id,
                date=date.today() + timedelta(days=3),
                time=time(20, 0),
                number_of_people=2,
                status="confirmed",
            ),
        ]
    )
    test_db.commit()

    items, total = crud.get_user_reservations(test_db, user_id=test_user.id)
    assert total == 1
    assert items[0].user_id == test_user.id


def test_get_user_reservations_filter_status(test_db, test_user, test_restaurant):
    test_db.add_all(
        [
            Reservation(
                user_id=test_user.id,
                restaurant_id=test_restaurant.id,
                date=date.today() + timedelta(days=3),
                time=time(19, 0),
                number_of_people=2,
                status="confirmed",
            ),
            Reservation(
                user_id=test_user.id,
                restaurant_id=test_restaurant.id,
                date=date.today() + timedelta(days=3),
                time=time(20, 0),
                number_of_people=2,
                status="cancelled",
            ),
        ]
    )
    test_db.commit()

    items, total = crud.get_user_reservations(
        test_db, user_id=test_user.id, status="cancelled"
    )
    assert total == 1
    assert items[0].status == "cancelled"


# ─── can_cancel : règle H-2 ──────────────────────────────────────────────────


def _fake_reservation(when: datetime) -> SimpleNamespace:
    return SimpleNamespace(date=when.date(), time=when.time().replace(microsecond=0))


@pytest.mark.parametrize("hours_ahead", [3, 5, 24, 24 * 7])
def test_can_cancel_far_enough_in_advance(hours_ahead):
    fake = _fake_reservation(datetime.now() + timedelta(hours=hours_ahead))
    assert crud.can_cancel(fake) is True


@pytest.mark.parametrize("hours_ahead", [0, 1])
def test_cannot_cancel_within_two_hours(hours_ahead):
    fake = _fake_reservation(datetime.now() + timedelta(hours=hours_ahead))
    assert crud.can_cancel(fake) is False


def test_cannot_cancel_past_reservation():
    fake = _fake_reservation(datetime.now() - timedelta(hours=1))
    assert crud.can_cancel(fake) is False


# ─── cancel_reservation ──────────────────────────────────────────────────────


def test_cancel_reservation_sets_status(test_db, test_user, test_restaurant):
    reservation = Reservation(
        user_id=test_user.id,
        restaurant_id=test_restaurant.id,
        date=date.today() + timedelta(days=7),
        time=time(19, 0),
        number_of_people=2,
        status="confirmed",
    )
    test_db.add(reservation)
    test_db.commit()

    updated = crud.cancel_reservation(test_db, reservation)
    assert updated.status == "cancelled"
