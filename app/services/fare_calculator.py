from typing import Tuple
import math
from app.core.config import settings

class FareCalculator:
    BASE_FARE = 10.0
    PER_KM_RATE = 2.0
    PER_MINUTE_RATE = 0.5
    SURGE_MULTIPLIER = 1.5

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float, unused_param: int = 0) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    @staticmethod
    def calculate_estimated_time(distance: float, avg_speed: float = 30.0) -> float:
        """Calculate estimated time in minutes"""
        return (distance / avg_speed) * 60

    @classmethod
    def calculate_fare(
        cls,
        pickup_location: Tuple[float, float],
        dropoff_location: Tuple[float, float],
        is_surge: bool = False,
        promo_code: str = None
    ) -> dict:
        """Calculate fare for a ride"""
        # Extract coordinates
        lat1, lon1 = pickup_location
        lat2, lon2 = dropoff_location

        # Calculate distance and time
        distance = cls.calculate_distance(lat1, lon1, lat2, lon2)
        estimated_time = cls.calculate_estimated_time(distance)

        # Calculate base fare
        distance_fare = distance * cls.PER_KM_RATE
        time_fare = estimated_time * cls.PER_MINUTE_RATE
        subtotal = cls.BASE_FARE + distance_fare + time_fare

        # Apply surge pricing if applicable
        if is_surge:
            subtotal *= cls.SURGE_MULTIPLIER

        # Calculate tax
        tax = subtotal * settings.TAX_RATE
        total = subtotal + tax

        return {
            "base_fare": cls.BASE_FARE,
            "distance_fare": round(distance_fare, 2),
            "time_fare": round(time_fare, 2),
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "distance": round(distance, 2),
            "estimated_time": round(estimated_time, 2),
            "is_surge": is_surge
        } 