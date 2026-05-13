from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.database import Base

from sqlalchemy.orm import relationship




class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = {"extend_existing": True}  # <--- Ajoutez cette ligne
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float)
    comment = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    restaurant = relationship("Restaurant", back_populates="reviews")




