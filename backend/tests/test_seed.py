"""Tests du seed des restaurants de démonstration."""

from __future__ import annotations

from app.models.restaurant import Restaurant
from app.seeds.seed_restaurants import _SEED_DATA, seed_restaurants


def test_seed_populates_empty_database(test_db):
    inserted = seed_restaurants(test_db)
    assert inserted == len(_SEED_DATA)
    assert test_db.query(Restaurant).count() == len(_SEED_DATA)


def test_seed_is_idempotent_on_count(test_db):
    seed_restaurants(test_db)
    second_pass = seed_restaurants(test_db)
    assert second_pass == 0
    assert test_db.query(Restaurant).count() == len(_SEED_DATA)


def test_seed_resyncs_missing_image_urls(test_db):
    # Premier seed normal, puis on casse un image_url en base
    seed_restaurants(test_db)
    target_name = _SEED_DATA[0]["name"]
    target = test_db.query(Restaurant).filter_by(name=target_name).one()
    target.image_url = None
    test_db.commit()

    # Le second passage doit ré-aligner l'URL sur le seed
    seed_restaurants(test_db)
    test_db.refresh(target)
    assert target.image_url == _SEED_DATA[0]["image_url"]


def test_seed_data_integrity():
    """Tous les seeds ont les champs requis."""
    for entry in _SEED_DATA:
        assert entry["name"]
        assert entry["cuisine"]
        assert entry["city"]
        assert 1 <= entry["price_range"] <= 4
        assert 0.0 <= entry["rating"] <= 5.0
        assert entry["image_url"].startswith("https://images.unsplash.com/photo-")
