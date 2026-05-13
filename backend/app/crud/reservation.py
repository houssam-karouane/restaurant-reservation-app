from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.reservation import Reservation

# ─── Vérification disponibilité ──────────────────────────────────────────────


def is_slot_available(
    db: Session,
    restaurant_id: int,
    date,
    time,
    number_of_people: int,
) -> bool:
    """
    Vérifie qu'il n'existe pas déjà une réservation confirmée
    pour ce restaurant à cette date/heure.
    """
    existing = (
        db.query(Reservation)
        .filter(
            and_(
                Reservation.restaurant_id == restaurant_id,
                Reservation.date == date,
                Reservation.time == time,
                Reservation.status.in_(["pending", "confirmed"]),
            )
        )
        .first()
    )
    return existing is None


# ─── Créer une réservation ────────────────────────────────────────────────────


def create_reservation(
    db: Session,
    user_id: int,
    restaurant_id: int,
    date,
    time,
    number_of_people: int,
) -> Reservation:
    reservation = Reservation(
        user_id=user_id,
        restaurant_id=restaurant_id,
        date=date,
        time=time,
        number_of_people=number_of_people,
        status="confirmed",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


# ─── Lister les réservations d'un user ───────────────────────────────────────


def get_user_reservations(
    db: Session,
    user_id: int,
    status: Optional[str] = None,
) -> Tuple[List[Reservation], int]:
    query = db.query(Reservation).filter(Reservation.user_id == user_id)
    if status:
        query = query.filter(Reservation.status == status)

    query = query.order_by(Reservation.date.desc())
    total = query.count()
    items = query.all()
    return items, total


# ─── Détail d'une réservation ─────────────────────────────────────────────────


def get_reservation_by_id(
    db: Session,
    reservation_id: int,
) -> Optional[Reservation]:
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


# ─── Annuler une réservation (règle H-2) ─────────────────────────────────────


def can_cancel(reservation: Reservation) -> bool:
    """
    Règle métier : annulation possible uniquement jusqu'à H-2.
    Combine date + time pour obtenir le datetime complet.
    """
    reservation_datetime = datetime.combine(
        reservation.date,
        reservation.time,
    )
    limit = reservation_datetime - timedelta(hours=2)
    return datetime.now() <= limit


def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
    reservation.status = "cancelled"
    db.commit()
    db.refresh(reservation)
    return reservation
