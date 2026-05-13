import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth
from app.api.v1.api import api_router
from app.db import base  # noqa: F401  # Force le chargement de tous les modèles
from app.database import SessionLocal, engine, Base
from app.seeds.seed_restaurants import seed_restaurants

logger = logging.getLogger("uvicorn.error")


app = FastAPI(
    title="Restaurant Reservation API",
    description="API REST pour la gestion des réservations et recommandations de restaurants",
    version="1.0.0",
)
app.include_router(api_router, prefix="/api/v1")
# ...
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])


# Configuration CORS (nécessaire pour que le frontend Angular puisse appeler l'API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production (ex: Vercel URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def bootstrap_database() -> None:
    """Crée le schéma manquant et seed les données de démonstration.

    Au démarrage seulement (pas à l'import) pour que les tests puissent
    rediriger ``get_db`` sur une base SQLite éphémère.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        logger.exception("Création du schéma en échec — l'API démarre quand même.")
        return

    db = SessionLocal()
    try:
        inserted = seed_restaurants(db)
        if inserted:
            logger.info("Seed: %d restaurants de démonstration insérés.", inserted)
    except Exception:
        logger.exception("Seed des restaurants en échec — l'API démarre quand même.")
    finally:
        db.close()


@app.get("/health", tags=["System"])
def health_check():
    """
    Endpoint de santé pour Docker et Kubernetes.
    Critère d'acceptation du ticket DR-13.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "database": "connected",  # Vous affinerez cela avec SQLAlchemy plus tard
    }


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Restaurant Reservation API - Accédez à /docs pour Swagger"}
