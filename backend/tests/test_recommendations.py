"""Tests pour GET /api/v1/recommendations/me — DR-34.

Couvre :
- ``test_recommendations_with_history`` : user avec réservations passées
  → algo de scoring actif, fallback=False, les cuisines préférées
  sortent en tête.
- ``test_recommendations_new_user`` : user sans historique
  → fallback activé, top 6 par rating.
- ``test_recommendations_cached`` : 2e appel sert le cache Redis.
"""

from __future__ import annotations

from datetime import date, time, timedelta

from app.models.reservation import Reservation
from app.models.restaurant import Restaurant


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _seed_restaurants(test_db) -> dict[str, Restaurant]:
    """Crée un petit catalogue déterministe : 3 cuisines × 3 niveaux de rating.

    Retourne un dict pour pouvoir cibler les restaurants depuis les tests
    sans dépendre des id auto-incrémentés.
    """
    cards = [
        # cuisine italienne — 3 restos, ratings variés
        ("Pasta Roma", "italienne", 4.8),
        ("Pasta Milano", "italienne", 4.2),
        ("Pasta Napoli", "italienne", 3.9),
        # cuisine japonaise — 3 restos
        ("Sushi Tokyo", "japonaise", 4.7),
        ("Sushi Osaka", "japonaise", 4.3),
        ("Sushi Kyoto", "japonaise", 4.0),
        # cuisine française — 3 restos
        ("Bistrot Lyon", "française", 4.9),
        ("Bistrot Paris", "française", 4.5),
        ("Bistrot Nice", "française", 4.0),
    ]
    out: dict[str, Restaurant] = {}
    for name, cuisine, rating in cards:
        r = Restaurant(
            name=name,
            cuisine=cuisine,
            city="Paris",
            price_range=2,
            rating=rating,
            review_count=10,
        )
        test_db.add(r)
        out[name] = r
    test_db.commit()
    for r in out.values():
        test_db.refresh(r)
    return out


# ─── 1. User avec historique → algo de scoring actif ─────────────────────────


def test_recommendations_with_history(test_db, test_client, test_user, auth_headers):
    """Le user a 2 réservations confirmées sur de l'italien.

    Attendu : pas de fallback, les restaurants italiens non-visités
    sortent avec un score élevé.
    """
    catalog = _seed_restaurants(test_db)

    # 2 réservations confirmées sur 2 restos italiens distincts → italienne
    # devient la cuisine préférée n°1.
    for r in (catalog["Pasta Roma"], catalog["Pasta Milano"]):
        test_db.add(
            Reservation(
                user_id=test_user.id,
                restaurant_id=r.id,
                date=date.today() - timedelta(days=10),
                time=time(20, 0),
                number_of_people=2,
                status="confirmed",
            )
        )
    test_db.commit()

    resp = test_client.get("/api/v1/recommendations/me", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["fallback"] is False
    assert body["from_cache"] is False
    assert body["total"] == len(body["items"])
    assert 1 <= len(body["items"]) <= 6

    # Les restos visités ne doivent PAS être recommandés.
    visited_ids = {catalog["Pasta Roma"].id, catalog["Pasta Milano"].id}
    returned_ids = {item["id"] for item in body["items"]}
    assert returned_ids.isdisjoint(visited_ids)

    # Le 1er résultat doit avoir un score > 0 (algo actif, pas du hasard).
    first = body["items"][0]
    assert first["score"] > 0
    # Et le 3e resto italien (non visité) doit être recommandé.
    assert catalog["Pasta Napoli"].id in returned_ids


# ─── 2. User sans historique → fallback top rated ────────────────────────────


def test_recommendations_new_user(test_db, test_client, test_user, auth_headers):
    """Sans aucune réservation, on tombe sur le fallback ``top 6 ratings``."""
    catalog = _seed_restaurants(test_db)

    resp = test_client.get("/api/v1/recommendations/me", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["fallback"] is True
    assert body["from_cache"] is False
    assert len(body["items"]) == 6

    # Trié par rating décroissant : le 1er doit être le mieux noté du catalogue.
    best = max(catalog.values(), key=lambda r: r.rating)
    assert body["items"][0]["id"] == best.id

    # Les ratings retournés doivent être décroissants.
    ratings = [item["rating"] for item in body["items"]]
    assert ratings == sorted(ratings, reverse=True)


# ─── 3. Cache Redis : 2e appel sert depuis le cache ──────────────────────────


def test_recommendations_cached(test_db, test_client, auth_headers, monkeypatch):
    """Le 2e GET doit renvoyer ``from_cache=True`` sans recalculer.

    On stubbe les helpers de cache au lieu d'utiliser un vrai Redis :
    - ``set_cached_recommendations`` écrit dans un dict en mémoire
    - ``get_cached_recommendations`` lit depuis ce dict
    Et on s'assure que ``compute_recommendations`` n'est appelé qu'une seule fois.
    """
    _seed_restaurants(test_db)

    store: dict[int, list[dict]] = {}
    compute_calls: list[int] = []

    def fake_get(user_id: int):
        return store.get(user_id)

    def fake_set(user_id: int, items: list[dict], ttl: int = 3600):
        store[user_id] = items

    # Wrap compute_recommendations to count invocations.
    import app.api.v1.endpoints.recommendations as endpoint_module
    import app.services.cache as cache_module

    real_compute = endpoint_module.compute_recommendations

    def counting_compute(*args, **kwargs):
        compute_calls.append(1)
        return real_compute(*args, **kwargs)

    monkeypatch.setattr(cache_module, "get_cached_recommendations", fake_get)
    monkeypatch.setattr(cache_module, "set_cached_recommendations", fake_set)
    monkeypatch.setattr(endpoint_module, "get_cached_recommendations", fake_get)
    monkeypatch.setattr(endpoint_module, "set_cached_recommendations", fake_set)
    monkeypatch.setattr(endpoint_module, "compute_recommendations", counting_compute)

    # 1er appel → compute + set du cache
    r1 = test_client.get("/api/v1/recommendations/me", headers=auth_headers)
    assert r1.status_code == 200, r1.text
    body1 = r1.json()
    assert body1["from_cache"] is False
    assert len(compute_calls) == 1
    assert len(store) == 1  # un user en cache

    # 2e appel → from_cache=True, compute NON rappelé
    r2 = test_client.get("/api/v1/recommendations/me", headers=auth_headers)
    assert r2.status_code == 200, r2.text
    body2 = r2.json()
    assert body2["from_cache"] is True
    assert len(compute_calls) == 1, "compute_recommendations doit être appelé 1x seulement"

    # Le payload des items doit être identique (même contenu, dans le même ordre)
    ids1 = [item["id"] for item in body1["items"]]
    ids2 = [item["id"] for item in body2["items"]]
    assert ids1 == ids2
