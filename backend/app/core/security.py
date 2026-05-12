from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
import os

# Configuration du hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Récupération des variables d'env
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_ignore_in_prod")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe saisi correspond au hash en base."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Transforme un mot de passe clair en hash sécurisé."""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Génère un jeton JWT signé."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt