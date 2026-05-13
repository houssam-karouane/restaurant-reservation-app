# app/db/base.py
from app.database import Base
from app.models.user import User
from app.models.reservation import Reservation
from app.models.restaurant import Restaurant  # <--- Ajout crucial
from app.models.table import Table            # <--- Ajoutez-le aussi
from app.models.review import Review          # <--- Et celui-ci