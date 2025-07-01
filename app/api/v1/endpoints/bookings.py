from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
from datetime import datetime

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.models.driver import Driver as DriverModel
from app.models.booking import Booking as BookingModel, BookingStatus
from app.schemas.booking import BookingCreate, BookingUpdate, Booking
from app.services.email import send_booking_confirmation, send_otp
from app.services.location_service import LocationService
from app.services.fare_calculator import FareCalculator
from app.services.driver_service import DriverService

router = APIRouter()

@router.post("/", response_model=Booking)
def create_booking(
    *,
    db: Session = Depends(get_db),
    booking_in: BookingCreate,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Create new booking.
    """
    # 1. Find nearby available drivers
    nearby_drivers = LocationService.find_nearby_drivers(db, booking_in.pickup_location)
    # 2. Calculate fare based on distance and time
    fare = FareCalculator.calculate_fare(booking_in.pickup_location, booking_in.dropoff_location)
    # 3. Assign a driver
    driver = DriverService.assign_driver(db, booking_in, fare, nearby_drivers)
    # For this example, we'll just create the bookin_in
    surgePricing = LocationService.check_surge_pricing(db,booking_in.pickup_location,"yes");
    fare['total'] = fare['total'] * surgePricing

    booking = BookingModel(
        user_id=current_user.id,
        pickup_location=booking_in.pickup_location,
        dropoff_location=booking_in.dropoff_location,
        scheduled_time=booking_in.scheduled_time,
        status=BookingStatus.PENDING,
        driver_id=driver.id,
        fare=fare['total'],
        distance=fare['distance'],
        duration=fare['duration'],
        cab_id=driver.cab_id,
        pickup_location=booking_in.pickup_location,
        dropoff_location=booking_in.dropoff_location,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Send confirmation email
    send_booking_confirmation(email_to=current_user.email, booking_id=booking.id)
    
    return booking

@router.get("/", response_model=List[Booking])
def read_bookings(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get all bookings for current user.
    """
    return current_user.bookings

@router.get("/{booking_id}", response_model=Booking)
def read_booking(
    *,
    db: Session = Depends(get_db),
    booking_id: str,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get specific booking.
    """
    booking = db.query(BookingModel).filter(
        BookingModel.id == booking_id,
        BookingModel.user_id == current_user.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}/cancel", response_model=Booking)
def cancel_booking(
    *,
    db: Session = Depends(get_db),
    booking_id: str,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Cancel booking.
    """
    booking = db.query(BookingModel).filter(
        BookingModel.id == booking_id,
        BookingModel.user_id == current_user.id
    ).first()
    driver = DriverService.get_driver_by_id(db, booking.driver_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if booking.status not in [BookingStatus.PENDING, BookingStatus.ACCEPTED]:
        raise HTTPException(status_code=400, detail="Cannot cancel booking in current status")
    
    booking.status = BookingStatus.CANCELLED
    booking.driver_id = None
    driver.is_available = True
    db.add(driver)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.put("/{booking_id}/start", response_model=Booking)
def start_ride(
    *,
    db: Session = Depends(get_db),
    booking_id: str,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Start ride (driver only).
    """
    driver = db.query(DriverModel).filter(DriverModel.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    booking = db.query(BookingModel).filter(
        BookingModel.id == booking_id,
        BookingModel.driver_id == driver.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != BookingStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Cannot start ride in current status")
    
    booking.status = BookingStatus.IN_PROGRESS
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    # Send OTP to user
    send_otp(email_to=booking.user.email, otp="123456")  # In real app, generate random OTP
    
    return booking

@router.put("/{booking_id}/complete", response_model=Booking)
def complete_ride(
    *,
    db: Session = Depends(get_db),
    booking_id: str,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Complete ride (driver only).
    """
    driver = db.query(DriverModel).filter(DriverModel.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    booking = db.query(BookingModel).filter(
        BookingModel.id == booking_id,
        BookingModel.driver_id == driver.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != BookingStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Cannot complete ride in current status")
    
    booking.status = BookingStatus.COMPLETED
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    # Update driver stats
    driver.total_rides += 1
    driver.total_earnings += booking.fare
    db.add(driver)
    db.commit()
    
    return booking 