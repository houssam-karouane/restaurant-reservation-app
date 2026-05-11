# Backend - FastAPI

API REST pour l''application Restaurant Reservation.

## Lancer en local (via Docker)

```bash
docker compose up backend
```

L''API sera disponible sur http://localhost:8000
La documentation Swagger sur http://localhost:8000/docs

## Structure
backend/
├── app/
│   ├── api/          Endpoints REST
│   ├── models/       Modeles SQLAlchemy
│   └── core/         Config, security, utils
├── tests/            Tests Pytest
├── Dockerfile
└── requirements.txt

## En cours (DR-13, DR-14)

Implementation en cours par ME :
- Modeles SQLAlchemy (User, Restaurant, Reservation)
- Migrations Alembic
- Endpoint /health
