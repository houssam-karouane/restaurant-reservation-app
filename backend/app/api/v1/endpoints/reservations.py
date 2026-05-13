from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import reservation as crud_reservation
from app.database import get_db
from app.models.user import User
from app.schemas.reservation import (
    ReservationCreate,
    ReservationListResponse,
    ReservationResponse,
)

router = APIRouter()


# ─── POST /reservations ───────────────────────────────────────────────────────


@router.post("", response_model=ReservationResponse, status_code=201)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Créer une réservation.
    Vérifie la disponibilité du créneau avant de confirmer.
    """
    # Vérifier disponibilité
    available = crud_reservation.is_slot_available(
        db=db,
        restaurant_id=payload.restaurant_id,
        date=payload.date,
        time=payload.time,
        number_of_people=payload.number_of_people,
    )
    if not available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce créneau n'est plus disponible",
        )

    return crud_reservation.create_reservation(
        db=db,
        user_id=current_user.id,
        restaurant_id=payload.restaurant_id,
        date=payload.date,
        time=payload.time,
        number_of_people=payload.number_of_people,
    )


# ─── GET /reservations/me ─────────────────────────────────────────────────────


@router.get("/me", response_model=ReservationListResponse)
def list_my_reservations(
    status: Optional[str] = Query(
        None, description="Filtrer par statut : pending / confirmed / cancelled"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste toutes les réservations de l'utilisateur connecté."""
    # Valider le statut si fourni
    valid_statuses = ["pending", "confirmed", "cancelled"]
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Statut invalide. Valeurs acceptées : {valid_statuses}",
        )

    items, total = crud_reservation.get_user_reservations(
        db=db,
        user_id=current_user.id,
        status=status,
    )
    return ReservationListResponse(items=items, total=total)


# ─── GET /reservations/{id} ───────────────────────────────────────────────────


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Détails d'une réservation — accessible uniquement par le propriétaire."""
    reservation = crud_reservation.get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Réservation #{reservation_id} introuvable")

    # Vérifier que c'est bien la réservation de l'utilisateur courant
    if reservation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit à cette réservation")

    return reservation


# ─── DELETE /reservations/{id} ───────────────────────────────────────────────


@router.delete("/{reservation_id}", status_code=200)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Annuler une réservation.
    Règle métier : annulation possible uniquement jusqu'à H-2.
    Seul le propriétaire peut annuler.
    """
    reservation = crud_reservation.get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Réservation #{reservation_id} introuvable")

    # Vérifier propriétaire
    if reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez pas annuler la réservation d'un autre utilisateur",
        )

    # Vérifier règle H-2
    if not crud_reservation.can_cancel(reservation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Annulation impossible : le créneau est dans moins de 2 heures",
        )

    crud_reservation.cancel_reservation(db=db, reservation=reservation)
    return {"message": "Réservation annulée avec succès"}
