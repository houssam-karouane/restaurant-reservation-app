from fastapi import APIRouter
from app.api.v1.endpoints import auth # Importe tes fichiers
from fastapi import APIRouter
from app.api.v1.endpoints import auth, restaurants

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])


# On regroupe tout ici
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
#api_router.include_router(users.router, prefix="/users", tags=["users"])
#api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])