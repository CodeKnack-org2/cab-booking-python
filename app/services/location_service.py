from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.driver import Driver
from app.models.booking import Booking
from app.services.fare_calculator import FareCalculator

class LocationService:
    @staticmethod
    def find_nearby_drivers(
        db: Session,
        location: Tuple[float, float],
        radius_km: float = 5.0,
        limit: int = 10
    ) -> List[Driver]:
        """Find available drivers within a radius"""
        # This is a simplified version. In production, you would use:
        # 1. Geospatial queries with PostGIS
        # 2. Redis for real-time location tracking
        # 3. Proper indexing for performance
        
        drivers = db.query(Driver).filter(
            Driver.is_available == True,
            Driver.is_active == True
        ).all()
        
        nearby_drivers = []
        for driver in drivers:
            distance = FareCalculator.calculate_distance(
                location, 
                driver.current_location 
            )
            if distance <= radius_km:
                nearby_drivers.append(driver)
                if len(nearby_drivers) >= limit:
                    break
        
        return nearby_drivers

    @staticmethod
    def update_driver_location(
        db: Session,
        driver_id: int,
        location: Tuple[float, float]
    ) -> None:
        """Update driver's current location"""
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if driver:
            driver.current_location = location
            db.commit()

    @staticmethod
    def get_booking_route(
        db: Session,
        booking_id: int
    ) -> Optional[dict]:
        """Get the route details for a booking"""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None

        # Calculate route details
        distance = FareCalculator.calculate_distance(
            booking.pickup_location[0], booking.pickup_location[1],
            booking.dropoff_location[0], booking.dropoff_location[1]
        )
        
        fare_info = FareCalculator.calculate_fare(
            booking.pickup_location, booking.dropoff_location
        )
        estimated_time = FareCalculator.calculate_estimated_time(fare_info)  # Should be distance (float)

        return {
            "pickup_location": booking.pickup_location,
            "dropoff_location": booking.dropoff_location,
            "distance": round(distance, 2),
            "estimated_time": round(estimated_time, 2)
        }

    @staticmethod
    def check_surge_pricing(
        db: Session,
        location: Tuple[float, float],
        radius_km: float = 2.0
    ) -> bool:
        """Check if surge pricing should be applied"""
        # This is a simplified version. In production, you would:
        # 1. Consider historical data
        # 2. Account for time of day
        # 3. Consider special events
        # 4. Use machine learning for prediction
        
        active_bookings = db.query(Booking).filter(
            Booking.status.in_(["PENDING", "ACCEPTED", "IN_PROGRESS"])
        ).all()
        
        booking_count = 0
        for booking in active_bookings:
            distance = FareCalculator.calculate_distance(
                location[0], location[1],
                booking.pickup_location[0], booking.pickup_location[1]
            )
            if distance <= radius_km:
                booking_count += 1
        
        # Apply surge if more than 5 bookings in the area
        fare_info = FareCalculator.calculate_fare(
            location[0], location[1], 
            booking.pickup_location[0], booking.pickup_location[1],
            is_surge=True
        )
        
        surge_status = booking_count > 5
        return int(surge_status) 