from fastapi import APIRouter
from app.api.v1.endpoints import auth, reservations, users
from app.api.v1.endpoints import restaurants

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
