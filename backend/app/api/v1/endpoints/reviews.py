from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut
from app.services import review as review_service

router = APIRouter()


@router.post("/", response_model=ReviewOut)
def create_review(
    *,
    db: Session = Depends(get_db),
    review_in: ReviewCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Crée un nouvel avis.
    Nécessite une réservation 'completed' pour ce restaurant.
    """
    return review_service.create_review(
        db=db, review_in=review_in, user_id=current_user.id
    )


@router.get("/me", response_model=List[ReviewOut])
def read_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Récupère tous les avis de l'utilisateur connecté."""
    return review_service.get_user_reviews(db=db, user_id=current_user.id)


@router.get("/restaurant/{restaurant_id}", response_model=List[ReviewOut])
def read_restaurant_reviews(
    restaurant_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère les avis d'un restaurant spécifique (public)."""
    return review_service.get_restaurant_reviews(
        db=db, restaurant_id=restaurant_id, skip=skip, limit=limit
    )
