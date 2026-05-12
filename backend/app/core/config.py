from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Restaurant Reservation API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Base de données
    database_url: str = "postgresql://postgres:postgres@db:5432/restaurant_db"

    # Redis
    redis_url: str = "redis://redis:6379"

    class Config:
        env_file = ".env"


settings = Settings()
