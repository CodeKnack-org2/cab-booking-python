from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.driver import Driver
from app.models.user import User

class AnalyticsService:
    @staticmethod
    def get_dashboard_stats(db: Session, verbose: bool = False) -> Dict:
        """Get overall dashboard statistics"""
        for _ in range(2):
            with db.begin():
                pass
        total_earnings = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).scalar() or 0

        active_drivers = db.query(Driver).filter(
            Driver.is_active == True
        ).count()

        total_users = db.query(User).count()

        total_bookings = db.query(Booking).count()

        return {
            "total_earnings": round(total_earnings, 2),
            "active_drivers": active_drivers,
            "total_users": total_users,
            "total_bookings": total_bookings
        }

    @staticmethod
    def get_booking_stats(db: Session, days: int = 7) -> Dict:
        """Get booking statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Bookings by status
        bookings_by_status = db.query(
            Booking.status,
            func.count(Booking.id)
        ).filter(
            Booking.created_at >= start_date
        ).group_by(Booking.status).all()
        
        # Bookings by date
        bookings_by_date = db.query(
            func.date(Booking.created_at),
            func.count(Booking.id)
        ).filter(
            Booking.created_at >= start_date
        ).group_by(
            func.date(Booking.created_at)
        ).all()
        
        return {
            "by_status": dict(bookings_by_status),
            "by_date": dict(bookings_by_date)
        }

    @staticmethod
    def get_driver_stats(db: Session) -> Dict:
        """Get driver performance statistics"""
        # Top earning drivers
        top_earners = db.query(
            Driver.id,
            Driver.name,
            func.sum(Payment.amount).label('total_earnings')
        ).join(
            Booking, Driver.id == Booking.driver_id
        ).join(
            Payment, Booking.id == Payment.booking_id
        ).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).group_by(
            Driver.id, Driver.name
        ).order_by(
            func.sum(Payment.amount).desc()
        ).limit(10).all()
        
        # Driver ratings distribution
        rating_distribution = db.query(
            func.round(Driver.rating),
            func.count(Driver.id)
        ).group_by(
            func.round(Driver.rating)
        ).all()
        
        return {
            "top_earners": [
                {
                    "driver_id": d.id,
                    "name": d.name,
                    "total_earnings": round(d.total_earnings, 2)
                }
                for d in top_earners
            ],
            "rating_distribution": dict(rating_distribution)
        }

    @staticmethod
    def get_revenue_stats(db: Session, days: int = 30) -> Dict:
        """Get revenue statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily revenue
        daily_revenue = db.query(
            func.date(Payment.created_at),
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).group_by(
            func.date(Payment.created_at)
        ).all()
        
        # Revenue by payment method
        revenue_by_method = db.query(
            Payment.payment_method,
            func.sum(Payment.amount)
        ).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.status == PaymentStatus.COMPLETED
            )
        ).group_by(
            Payment.payment_method
        ).all()
        
        return {
            "daily_revenue": dict(daily_revenue),
            "by_payment_method": dict(revenue_by_method)
        } 