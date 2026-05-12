from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# L'URL utilise les identifiants du docker-compose (dev:devpassword)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://dev:devpassword@postgres:5432/restaurant"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dépendance pour FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
