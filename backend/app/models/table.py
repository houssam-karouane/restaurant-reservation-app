from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Table(Base):
    __tablename__ = "tables"
    __table_args__ = {"extend_existing": True}  # <--- Ajoutez cette ligne précise
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String)  # Numéro de la table (ex: "Table 5")
    capacity = Column(Integer)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    restaurant = relationship("Restaurant", back_populates="tables")
