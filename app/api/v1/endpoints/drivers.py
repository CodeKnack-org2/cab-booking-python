from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.models.driver import Driver as DriverModel
from app.schemas.driver import DriverCreate, DriverUpdate, Driver
from app.services.location_service import LocationService

router = APIRouter()

@router.post("/", response_model=Driver)
def create_driver(
    *,
    db: Session = Depends(get_db),
    driver_in: DriverCreate,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Create new driver profile.
    """
    driver = DriverModel(
        user_id=current_user.id,
        license_number=driver_in.license_number,
        current_location=driver_in.current_location,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver

@router.get("/me", response_model=Driver)
def read_driver_me(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get current driver profile.
    """
    driver = db.query(DriverModel).filter(DriverModel.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    return driver

@router.put("/me", response_model=Driver)
def update_driver_me(
    *,
    db: Session = Depends(get_db),
    driver_in: DriverUpdate,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Update current driver profile.
    """
    driver = db.query(DriverModel).filter(DriverModel.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    for field, value in driver_in.dict(exclude_unset=True).items():
        setattr(driver, field, value)
    
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver

@router.put("/me/availability", response_model=Driver)
def update_availability(
    *,
    db: Session = Depends(get_db),
    is_available: bool,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Update driver availability.
    """
    driver = db.query(DriverModel).filter(DriverModel.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    driver.is_available = is_available
    db.add(driver)
    db.commit()
    db.refresh(driver)
    
    LocationService.update_driver_location(
        db=db,
        driver_id=str(driver.id), 
        location=driver.current_location
    )
    
    return driver

@router.get("/me/earnings", response_model=dict)
def read_earnings(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get driver earnings.
    """
    driver = db.query(DriverModel).filter(DriverModel.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    return {
        "total_earnings": driver.total_earnings,
        "total_rides": driver.total_rides,
        "rating": driver.rating
    } 