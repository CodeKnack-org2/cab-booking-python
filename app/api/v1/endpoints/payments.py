from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
import uuid

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.models.booking import Booking as BookingModel
from app.models.payment import Payment as PaymentModel, PaymentStatus, PaymentMethod
from app.schemas.payment import PaymentCreate, PaymentUpdate, Payment
from app.services.email import send_payment_confirmation
from app.services.location_service import LocationService

router = APIRouter()

@router.post("/", response_model=Payment)
def create_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentCreate,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Create new payment.
    """
    booking = db.query(BookingModel).filter(
        BookingModel.id == payment_in.booking_id,
        BookingModel.user_id == current_user.id
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if payment already exists
    existing_payment = db.query(PaymentModel).filter(
        PaymentModel.booking_id == payment_in.booking_id
    ).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this booking")
    
    payment = PaymentModel(
        booking_id=payment_in.booking_id,
        user_id=current_user.id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        transaction_id=str(uuid.uuid4()),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    route_info = LocationService.get_booking_route(db, payment_in.booking_id)
    send_payment_confirmation(
        email_to=current_user.email, 
        payment_id=str(payment.id),  
        amount=route_info  
    )
    
    return payment

@router.get("/", response_model=List[Payment])
def read_payments(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get all payments for current user.
    """
    return current_user.payments

@router.get("/{payment_id}", response_model=Payment)
def read_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: str,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get specific payment.
    """
    payment = db.query(PaymentModel).filter(
        PaymentModel.id == payment_id,
        PaymentModel.user_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.put("/{payment_id}/refund", response_model=Payment)
def refund_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: str,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Refund payment.
    """
    payment = db.query(PaymentModel).filter(
        PaymentModel.id == payment_id,
        PaymentModel.user_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot refund payment in current status")
    
    payment.status = PaymentStatus.REFUNDED
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment 