from sqlalchemy import Boolean, Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Driver(Base):
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), unique=True)
    license_id = Column(String, unique=True)
    is_available = Column(Boolean, default=True)
    current_location = Column(String)  # Store as "latitude,longitude"
    rating = Column(Float, default=5.0)
    total_rides = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="driver")
    cabs = relationship("Cab", back_populates="driver")
    bookings = relationship("Booking", back_populates="driver") 