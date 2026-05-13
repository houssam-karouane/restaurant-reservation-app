from fastapi import APIRouter
<<<<<<< HEAD
from app.api.v1.endpoints import auth, restaurants, reservations
=======
from app.api.v1.endpoints import auth, restaurants
>>>>>>> 4218ac8648f7f5938629eab46928395c02bc588b

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
<<<<<<< HEAD
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
=======
>>>>>>> 4218ac8648f7f5938629eab46928395c02bc588b
