"""
Backend FastAPI - Placeholder Sprint 1
Sera complete par ME via DR-13 (FastAPI proper) et DR-14 (modeles SQLAlchemy).
"""
from fastapi import FastAPI

app = FastAPI(
    title="Restaurant Reservation API",
    description="API REST pour reservation de restaurants - Placeholder Sprint 1",
    version="0.0.1"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Backend placeholder - waiting for DR-13",
        "version": "0.0.1"
    }


@app.get("/")
def root():
    return {"message": "Restaurant Reservation API - see /docs for Swagger UI"}