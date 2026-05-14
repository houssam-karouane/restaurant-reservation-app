from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationResponse,
)
from app.services.recommendation import compute_recommendations
from app.services.cache import (
    get_cached_recommendations,
    set_cached_recommendations,
)

router = APIRouter()


@router.get("/me", response_model=RecommendationResponse)
def get_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retourne 6 restaurants recommandés personnalisés.

    Algorithme :
    - Score 1 : cuisines préférées (basé sur réservations passées)
    - Score 2 : restaurants des users similaires
    - Score 3 : restaurants notés > 4.5/5

    Cache Redis TTL 1h — clé : recommendations:{user_id}
    Fallback automatique si aucun historique.
    """
    user_id = current_user.id

    # 1. Vérifier le cache Redis
    cached = get_cached_recommendations(user_id)
    if cached:
        return RecommendationResponse(
            items=[RecommendationItem(**item) for item in cached],
            total=len(cached),
            from_cache=True,
            fallback=False,
        )

    # 2. Calculer les recommandations
    items, is_fallback = compute_recommendations(db=db, user_id=user_id)

    # 3. Mettre en cache
    set_cached_recommendations(user_id, items)

    return RecommendationResponse(
        items=[RecommendationItem(**item) for item in items],
        total=len(items),
        from_cache=False,
        fallback=is_fallback,
    )
