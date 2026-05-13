from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    number_of_people = Column(Integer, nullable=False)    
    status = Column(String, default="pending")  # pending, confirmed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations pour faciliter les requêtes
    user = relationship("User", back_populates="reservations")
    restaurant = relationship("Restaurant", back_populates="reservations")
