from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base_class import Base

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Booking(Base):
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"))
    driver_id = Column(String, ForeignKey("driver.id"))
    cab_id = Column(String, ForeignKey("cab.id"))
    pickup_location = Column(String)  # Store as "latitude,longitude"
    dropoff_location = Column(String)  # Store as "latitude,longitude"
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    fare = Column(Float)
    distance = Column(Float)  # in kilometers
    duration = Column(Float)  # in minutes
    scheduled_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    driver = relationship("Driver", back_populates="bookings")
    cab = relationship("Cab", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False) 