from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime, date, time


class ReservationCreate(BaseModel):
    """Payload POST /reservations."""

    restaurant_id: int
    date: date
    time: time
    number_of_people: int = Field(..., ge=1, le=20)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "restaurant_id": 1,
                "date": "2026-05-20",
                "time": "19:30:00",
                "number_of_people": 2,
            }
        }
    )


class ReservationResponse(BaseModel):
    """Réponse lecture d'une réservation."""

    id: int
    restaurant_id: int
    user_id: int
    date: date
    time: time
    number_of_people: int
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReservationListResponse(BaseModel):
    """Liste des réservations de l'utilisateur courant."""

    items: List[ReservationResponse]
    total: int
