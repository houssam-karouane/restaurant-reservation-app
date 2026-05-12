from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# Schéma de base partagé
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

# Données requises pour l'inscription (Register)
class UserCreate(UserBase):
    password: str

# Données renvoyées par l'API (on cache le password !)
class UserResponse(UserBase):
    id: int
    is_active: bool = True

    # Permet la conversion automatique depuis l'objet SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# Schéma pour la connexion (Login)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schéma pour le Token JWT renvoyé après login
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None