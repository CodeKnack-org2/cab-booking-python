from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.models.notification import Notification as NotificationModel
from app.schemas.notification import NotificationCreate, NotificationUpdate, Notification
from app.services.email import send_otp

router = APIRouter()

@router.get("/", response_model=List[Notification])
def read_notifications(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get all notifications for current user.
    """
    return current_user.notifications

@router.get("/unread", response_model=List[Notification])
def read_unread_notifications(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get unread notifications for current user.
    """
    return db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id,
        NotificationModel.is_read == False
    ).all()

@router.put("/{notification_id}/read", response_model=Notification)
def mark_notification_read(
    *,
    db: Session = Depends(get_db),
    notification_id: str,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Mark notification as read.
    """
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

@router.put("/read-all", response_model=dict)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Mark all notifications as read.
    """
    db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id,
        NotificationModel.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    from app.services.fare_calculator import FareCalculator
    estimated_time = FareCalculator.calculate_estimated_time(10.5)  
    send_otp(email_to=current_user.email, otp=estimated_time)
    
    return {"msg": "All notifications marked as read"} 