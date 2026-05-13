from typing import Optional, Tuple, List
import math
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


def get_restaurants(
    db: Session,
    page: int = 1,
    limit: int = 10,
    cuisine: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
    city: Optional[str] = None,
) -> Tuple[List[Restaurant], int]:
    limit = min(limit, 50)
    query = db.query(Restaurant)

    if cuisine:
        query = query.filter(func.lower(Restaurant.cuisine) == func.lower(cuisine))
    if min_price is not None:
        query = query.filter(Restaurant.price_range >= min_price)
    if max_price is not None:
        query = query.filter(Restaurant.price_range <= max_price)
    if min_rating is not None:
        query = query.filter(Restaurant.rating >= min_rating)
    if city:
        query = query.filter(func.lower(Restaurant.city) == func.lower(city))

    query = query.order_by(Restaurant.rating.desc())
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


def get_restaurant_by_id(db: Session, restaurant_id: int) -> Optional[Restaurant]:
    return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()


def create_restaurant(db: Session, restaurant_in: RestaurantCreate) -> Restaurant:
    db_r = Restaurant(
        name=restaurant_in.name,
        address=restaurant_in.address,
        city=restaurant_in.city,
        cuisine=restaurant_in.cuisine,
        price_range=restaurant_in.price_range,
        rating=restaurant_in.rating or 0.0,
    )
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r


def update_restaurant(
    db: Session,
    restaurant: Restaurant,
    update_data: RestaurantUpdate,
) -> Restaurant:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, value)
    db.commit()
    db.refresh(restaurant)
    return restaurant


def delete_restaurant(db: Session, restaurant: Restaurant) -> None:
    db.delete(restaurant)
    db.commit()
