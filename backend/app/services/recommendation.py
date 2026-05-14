"""
Moteur de recommandations — DR-34
Algorithme combinant 3 scores sans ML lourd :
  Score 1 — cuisines préférées du user (basé sur ses réservations passées)
  Score 2 — restaurants des users similaires (mêmes préférences cuisines)
  Score 3 — top restaurants notés > 4.5/5
"""

from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.restaurant import Restaurant
from app.models.reservation import Reservation

# ─── Score 1 : cuisines préférées du user ────────────────────────────────────


def get_user_preferred_cuisines(
    db: Session,
    user_id: int,
) -> List[str]:
    """
    Retourne les types de cuisine que le user a le plus réservés,
    triés par fréquence décroissante.
    """
    results = (
        db.query(Restaurant.cuisine, func.count(Reservation.id).label("count"))
        .join(Reservation, Reservation.restaurant_id == Restaurant.id)
        .filter(Reservation.user_id == user_id)
        .filter(Reservation.status.in_(["confirmed", "completed"]))
        .group_by(Restaurant.cuisine)
        .order_by(func.count(Reservation.id).desc())
        .all()
    )
    return [r.cuisine for r in results]


def score_by_preferred_cuisine(
    restaurant: Restaurant,
    preferred_cuisines: List[str],
) -> float:
    """
    Score 1 : +3.0 si cuisine préférée #1, +2.0 si #2, +1.0 si #3+
    """
    if not preferred_cuisines:
        return 0.0
    if restaurant.cuisine == preferred_cuisines[0]:
        return 3.0
    if len(preferred_cuisines) > 1 and restaurant.cuisine == preferred_cuisines[1]:
        return 2.0
    if restaurant.cuisine in preferred_cuisines[2:]:
        return 1.0
    return 0.0


# ─── Score 2 : users similaires ──────────────────────────────────────────────


def get_similar_users_restaurant_ids(
    db: Session,
    user_id: int,
    preferred_cuisines: List[str],
) -> List[int]:
    """
    Trouve les users qui ont les mêmes préférences cuisine,
    retourne les IDs des restaurants qu'ils ont réservés
    (que le user courant n'a pas encore visités).
    """
    if not preferred_cuisines:
        return []

    # Users ayant réservé dans les mêmes cuisines
    similar_user_ids = (
        db.query(Reservation.user_id)
        .join(Restaurant, Restaurant.id == Reservation.restaurant_id)
        .filter(Restaurant.cuisine.in_(preferred_cuisines))
        .filter(Reservation.user_id != user_id)
        .filter(Reservation.status.in_(["confirmed", "completed"]))
        .distinct()
        .all()
    )
    similar_ids = [r.user_id for r in similar_user_ids]

    if not similar_ids:
        return []

    # Restaurants réservés par ces users similaires
    restaurant_ids = (
        db.query(Reservation.restaurant_id)
        .filter(Reservation.user_id.in_(similar_ids))
        .filter(Reservation.status.in_(["confirmed", "completed"]))
        .distinct()
        .all()
    )
    return [r.restaurant_id for r in restaurant_ids]


def score_by_similar_users(
    restaurant: Restaurant,
    similar_restaurant_ids: List[int],
) -> float:
    """Score 2 : +2.0 si recommandé par des users similaires."""
    return 2.0 if restaurant.id in similar_restaurant_ids else 0.0


# ─── Score 3 : note > 4.5 ───────────


def score_by_rating(restaurant: Restaurant) -> float:
    """Score 3 : +1.0 par 0.1 point au-dessus de 4.5 (max +5.0)."""
    if restaurant.rating and restaurant.rating > 4.5:
        return min((restaurant.rating - 4.5) * 10, 5.0)
    return 0.0


# ─── Moteur principal ─────────


def compute_recommendations(
    db: Session,
    user_id: int,
    limit: int = 6,
) -> Tuple[List[dict], bool]:
    """
    Calcule et retourne les `limit` meilleures recommandations.
    Retourne (items, is_fallback).

    Fallback activé si le user n'a aucun historique de réservation.
    """
    # Récupérer les préférences du user
    preferred_cuisines = get_user_preferred_cuisines(db, user_id)
    is_fallback = len(preferred_cuisines) == 0

    # Restaurants déjà visités par le user
    already_visited = (
        db.query(Reservation.restaurant_id)
        .filter(Reservation.user_id == user_id)
        .filter(Reservation.status.in_(["confirmed", "completed"]))
        .distinct()
        .all()
    )
    visited_ids = {r.restaurant_id for r in already_visited}

    # Tous les restaurants actifs (non déjà visités)
    restaurants = (
        db.query(Restaurant)
        .filter(Restaurant.id.notin_(visited_ids) if visited_ids else True)
        .all()
    )

    if is_fallback:
        # Fallback : top 6 restaurants par note
        top = sorted(restaurants, key=lambda r: r.rating or 0, reverse=True)[:limit]
        return [
            {
                "id": r.id,
                "name": r.name,
                "cuisine": r.cuisine,
                "city": r.city,
                "price_range": r.price_range,
                "rating": r.rating or 0.0,
                "score": r.rating or 0.0,
                "score_reason": "top rated",
            }
            for r in top
        ], True

    # Calculer les IDs recommandés par users similaires
    similar_ids = get_similar_users_restaurant_ids(db, user_id, preferred_cuisines)

    # Calculer le score combiné pour chaque restaurant
    scored = []
    for r in restaurants:
        s1 = score_by_preferred_cuisine(r, preferred_cuisines)
        s2 = score_by_similar_users(r, similar_ids)
        s3 = score_by_rating(r)
        total_score = s1 + s2 + s3

        reason_parts = []
        if s1 > 0:
            reason_parts.append(f"cuisine préférée ({r.cuisine})")
        if s2 > 0:
            reason_parts.append("users similaires")
        if s3 > 0:
            reason_parts.append(f"note {r.rating}")

        scored.append(
            {
                "id": r.id,
                "name": r.name,
                "cuisine": r.cuisine,
                "city": r.city,
                "price_range": r.price_range,
                "rating": r.rating or 0.0,
                "score": round(total_score, 2),
                "score_reason": (
                    ", ".join(reason_parts) if reason_parts else "découverte"
                ),
            }
        )

    # Trier par score décroissant, prendre les 6 premiers
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit], False
