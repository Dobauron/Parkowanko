# validators.py
from functools import wraps
from rest_framework.exceptions import ValidationError
from parking_point.models import ParkingPoint
from parking_point.utils.geo_utils import haversine


# ---------------------------------------------------------
# Dekorator 1: poprawna struktura location
# ---------------------------------------------------------
def reject_invalid_location_structure(func):
    @wraps(func)
    def wrapper(self, location):
        if not isinstance(location, dict):
            raise ValidationError("Pole 'location' musi być obiektem JSON.")

        if "lat" not in location or "lng" not in location:
            raise ValidationError("Pole 'location' musi zawierać klucze 'lat' i 'lng'.")

        try:
            float(location["lat"])
            float(location["lng"])
        except (ValueError, TypeError):
            raise ValidationError("Wartości 'lat' i 'lng' muszą być liczbami.")

        return func(self, location)

    return wrapper


