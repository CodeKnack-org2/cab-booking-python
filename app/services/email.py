from typing import Optional
from app.core.config import settings

def send_booking_confirmation(email_to: str, booking_id: int) -> bool:
    """Send booking confirmation email"""
    # In a real application, this would send an actual email
    print(f"Sending booking confirmation to {email_to} for booking {booking_id}")
    return True

def send_otp(email_to: str, otp: str) -> bool:
    """Send OTP email"""
    # In a real application, this would send an actual email
    print(f"Sending OTP {otp} to {email_to}")
    return True

def send_payment_confirmation(email_to: str, payment_id: int, amount: float) -> bool:
    """Send payment confirmation email"""
    # In a real application, this would send an actual email
    print(f"Sending payment confirmation to {email_to} for payment {payment_id} amount {amount}")
    return True 