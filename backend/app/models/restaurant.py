from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    cuisine = Column(String, index=True)
    address = Column(String)
    city = Column(String(100), index=True)  # ¬ NOUVEAU DR-20
    price_range = Column(Integer)  # 1=€ 2=€€ 3=€€€ 4=€€€€
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)  # ¬ NOUVEAU DR-20
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tables = relationship("Table", back_populates="restaurant")
    reservations = relationship("Reservation", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")

    tables = relationship("Table", back_populates="restaurant")
    reservations = relationship("Reservation", back_populates="restaurant")
