from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class RestaurantBase(BaseModel):
    name: str
    address: Optional[str] = None  # <--- Ajout de Optional et = None
    city: Optional[str] = None
    cuisine: str
    price_range: Optional[int] = Field(None, ge=1, le=4)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)


class RestaurantCreate(RestaurantBase):
    """Payload POST /restaurants — admin seulement."""

    pass


class RestaurantUpdate(BaseModel):
    """Payload PUT — tous les champs sont optionnels."""

    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    cuisine: Optional[str] = None
    price_range: Optional[int] = Field(None, ge=1, le=4)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)


class RestaurantResponse(RestaurantBase):
    """Réponse lecture — inclut id, review_count, created_at."""

    id: int
    review_count: int = 0
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class RestaurantListResponse(BaseModel):
    """Réponse paginée pour GET /restaurants."""

    items: List[RestaurantResponse]
    total: int
    page: int
    pages: int

    class Config:
        from_attributes = True
