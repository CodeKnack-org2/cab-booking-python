from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.driver import Driver
from app.models.booking import Booking
from app.services.fare_calculator import FareCalculator

class DriverService:
    @staticmethod
    def assign_driver(
        db: Session,
        booking: Booking,
        fare: dict,
        nearby_drivers: List[Driver]
    ) -> Driver:
        """Find available drivers within a radius"""
        nearest_driver = None
        min_distance = float('inf')

        for driver in nearby_drivers:
            distance = FareCalculator.calculate_distance(
                booking.pickup_location[0], booking.pickup_location[1],
                driver.current_location[0], driver.current_location[1]
            )
            if distance < min_distance:
                min_distance = distance
                nearest_driver = driver

        return nearest_driver