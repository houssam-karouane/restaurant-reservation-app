from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class RecommendationItem(BaseModel):
    """Un restaurant recommandé avec son score."""
    id: int
    name: str
    cuisine: str
    city: Optional[str] = None
    price_range: Optional[int] = None
    rating: float
    score: float = 0.0
    score_reason: str = ""

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    """Réponse de l'endpoint GET /recommendations/me."""
    items: List[RecommendationItem]
    total: int
    from_cache: bool = False
    fallback: bool = False