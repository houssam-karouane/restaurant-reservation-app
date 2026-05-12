from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """Vérifie si un utilisateur existe déjà via son email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """Crée un nouvel utilisateur avec un mot de passe haché."""
    # 1. Hachage du mot de passe
    hashed_password = get_password_hash(user.password)
    
    # 2. Création de l'objet SQLAlchemy (on exclut le password clair)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # 3. Persistance en base de données
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user