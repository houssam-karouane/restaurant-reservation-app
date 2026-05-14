"""
Cache Redis pour les recommandations — DR-34
Clé : recommendations:{user_id}
TTL : 1 heure
"""

import json
from typing import Optional, List
import redis
from app.core.config import settings


def get_redis_client():
    """Retourne un client Redis connecté."""
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cached_recommendations(user_id: int) -> Optional[List[dict]]:
    """
    Récupère les recommandations depuis Redis.
    Retourne None si pas en cache ou si Redis est indisponible.
    """
    try:
        r = get_redis_client()
        key = f"recommendations:{user_id}"
        data = r.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        # Redis indisponible → continuer sans cache
        return None


def set_cached_recommendations(
    user_id: int,
    recommendations: List[dict],
    ttl: int = 3600,  # 1 heure
) -> None:
    """
    Stocke les recommandations dans Redis avec TTL 1h.
    Silencieux si Redis est indisponible.
    """
    try:
        r = get_redis_client()
        key = f"recommendations:{user_id}"
        r.setex(key, ttl, json.dumps(recommendations))
    except Exception:
        pass


def invalidate_recommendations(user_id: int) -> None:
    """Invalide le cache quand l'utilisateur fait une nouvelle réservation."""
    try:
        r = get_redis_client()
        r.delete(f"recommendations:{user_id}")
    except Exception:
        pass
