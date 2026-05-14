from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.review import Review
from app.models.restaurant import Restaurant
from app.models.reservation import Reservation
from app.schemas.review import ReviewCreate


def update_restaurant_rating(db: Session, restaurant_id: int):
    """Calcule la moyenne des avis et met à jour le restaurant."""
    avg_rating = (
        db.query(func.avg(Review.rating))
        .filter(Review.restaurant_id == restaurant_id)
        .scalar()
    )

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if restaurant:
        # On arrondit à 1 décimale (ex: 4.56 -> 4.6)
        restaurant.rating = round(float(avg_rating), 1) if avg_rating else 0.0
        db.add(restaurant)
        db.commit()


def create_review(db: Session, review_in: ReviewCreate, user_id: int):
    """
    Crée un avis après avoir vérifié que l'utilisateur
    a bien une réservation terminée.
    """
    # 1. Vérification : Le user a-t-il mangé là-bas ?
    has_completed_reservation = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == user_id,
            Reservation.restaurant_id == review_in.restaurant_id,
            Reservation.status == "completed",
        )
        .first()
    )

    if not has_completed_reservation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez avoir une réservation terminée pour laisser un avis.",
        )

    # 2. Création de l'avis
    db_review = Review(**review_in.model_dump(), user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # 3. Side Effect : Mise à jour de la note du restaurant
    update_restaurant_rating(db, review_in.restaurant_id)

    return db_review


def get_restaurant_reviews(
    db: Session, restaurant_id: int, skip: int = 0, limit: int = 10
):
    """Récupère les avis d'un restaurant avec pagination."""
    return (
        db.query(Review)
        .filter(Review.restaurant_id == restaurant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_reviews(db: Session, user_id: int):
    """Récupère tous les avis d'un utilisateur."""
    return db.query(Review).filter(Review.user_id == user_id).all()
