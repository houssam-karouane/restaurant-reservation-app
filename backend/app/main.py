from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Restaurant Reservation API",
    description="API REST pour la gestion des réservations et recommandations de restaurants",
    version="1.0.0",
)

# Configuration CORS (nécessaire pour que le frontend Angular puisse appeler l'API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production (ex: Vercel URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
