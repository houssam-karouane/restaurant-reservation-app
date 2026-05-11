from pydantic import BaseModel
from typing import Optional

# Ce qui est commun à la lecture et à la création
class RestaurantBase(BaseModel):
    name: str
    address: str
    cuisine: str
    description: Optional[str] = None

# Ce qu'on reçoit lors de la création (POST)
class RestaurantCreate(RestaurantBase):
    pass

# Ce qu'on renvoie au client (GET) - inclut l'ID généré par la DB
class Restaurant(RestaurantBase):
    id: int

    class Config:
        from_attributes = True