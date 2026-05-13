from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    cuisine = Column(String, index=True)
    address = Column(String)
    price_range = Column(Integer)  # ex: 1 pour bon marché, 3 pour luxe
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tables = relationship("Table", back_populates="restaurant")
    reservations = relationship("Reservation", back_populates="restaurant")
