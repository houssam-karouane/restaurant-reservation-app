from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    """Champs communs pour les avis."""

    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    comment: Optional[str] = Field(None, max_length=500)
    restaurant_id: int


class ReviewCreate(ReviewBase):
    """Schéma pour la création d'un avis (POST)."""

    pass


class ReviewOut(ReviewBase):
    """Schéma pour l'affichage d'un avis (Réponse API)."""

    id: int
    user_id: int
    created_at: Optional[datetime] = None

    # Permet de convertir les modèles SQLAlchemy en Pydantic automatiquement
    model_config = ConfigDict(from_attributes=True)


class ReviewUpdate(BaseModel):
    """Optionnel : Pour modifier un avis existant."""

    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
