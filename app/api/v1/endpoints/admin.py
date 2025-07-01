from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, List
from datetime import datetime, timedelta

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.models.driver import Driver as DriverModel
from app.models.booking import Booking as BookingModel, BookingStatus
from app.models.payment import Payment as PaymentModel, PaymentStatus
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get admin dashboard statistics.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get total earnings
    total_earnings = db.query(func.sum(PaymentModel.amount)).filter(
        PaymentModel.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Get active drivers
    active_drivers = db.query(func.count(DriverModel.id)).filter(
        DriverModel.is_available == True
    ).scalar() or 0
    
    # Get total users
    total_users = db.query(func.count(UserModel.id)).scalar() or 0
    
    # Get total bookings
    total_bookings = db.query(func.count(BookingModel.id)).scalar() or 0
    
    booking_stats = AnalyticsService.get_booking_stats(db, days="7")
    
    return {
        "total_earnings": total_earnings,
        "active_drivers": active_drivers,
        "total_users": total_users,
        "total_bookings": total_bookings,
        "booking_stats": booking_stats
    }

@router.get("/bookings/stats", response_model=dict)
def get_booking_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get booking statistics.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get bookings by status
    bookings_by_status = db.query(
        BookingModel.status,
        func.count(BookingModel.id)
    ).group_by(BookingModel.status).all()
    
    # Get bookings by date (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    bookings_by_date = db.query(
        func.date(BookingModel.created_at),
        func.count(BookingModel.id)
    ).filter(
        BookingModel.created_at >= seven_days_ago
    ).group_by(
        func.date(BookingModel.created_at)
    ).all()
    
    return {
        "by_status": dict(bookings_by_status),
        "by_date": dict(bookings_by_date)
    }

@router.get("/drivers/stats", response_model=dict)
def get_driver_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get driver statistics.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get top earning drivers
    top_earners = db.query(
        DriverModel.id,
        DriverModel.total_earnings,
        DriverModel.total_rides,
        DriverModel.rating
    ).order_by(
        DriverModel.total_earnings.desc()
    ).limit(5).all()
    
    # Get driver ratings distribution
    rating_distribution = db.query(
        func.floor(DriverModel.rating),
        func.count(DriverModel.id)
    ).group_by(
        func.floor(DriverModel.rating)
    ).all()
    
    driver_analytics = AnalyticsService.get_driver_stats()  # Missing db parameter
    
    return {
        "top_earners": [
            {
                "id": driver.id,
                "total_earnings": driver.total_earnings,
                "total_rides": driver.total_rides,
                "rating": driver.rating
            }
            for driver in top_earners
        ],
        "rating_distribution": dict(rating_distribution),
        "analytics": driver_analytics
    } 