import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.crud import restaurant as crud_restaurant
from app.database import get_db
from app.models.user import User
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantListResponse,
    RestaurantResponse,
    RestaurantUpdate,
)

router = APIRouter()


@router.get("", response_model=RestaurantListResponse)
def list_restaurants(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    cuisine: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, ge=1, le=4),
    max_price: Optional[int] = Query(None, ge=1, le=4),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0),
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    items, total = crud_restaurant.get_restaurants(
        db=db,
        page=page,
        limit=limit,
        cuisine=cuisine,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        city=city,
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    return RestaurantListResponse(items=items, total=total, page=page, pages=pages)


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = crud_restaurant.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant #{restaurant_id} introuvable")
    return restaurant


@router.post("", response_model=RestaurantResponse, status_code=201)
def create_restaurant(
    restaurant_in: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs")
    return crud_restaurant.create_restaurant(db=db, restaurant_in=restaurant_in)


@router.put("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    update_data: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs")
    restaurant = crud_restaurant.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant #{restaurant_id} introuvable")
    return crud_restaurant.update_restaurant(db=db, restaurant=restaurant, update_data=update_data)


@router.delete("/{restaurant_id}", status_code=204)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs")
    restaurant = crud_restaurant.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant #{restaurant_id} introuvable")
    crud_restaurant.delete_restaurant(db=db, restaurant=restaurant)
