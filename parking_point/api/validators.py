# validators.py
from functools import wraps
from rest_framework.exceptions import ValidationError


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


# # ---------------------------------------------------------
# # Dekorator 3: nie za blisko innych punktów
# # ---------------------------------------------------------
# def reject_too_close_to_other_points(distance_limit=30):
#     """
#     distance_limit – minimalna odległość w metrach
#     """
#
#     def decorator(func):
#         @wraps(func)
#         def wrapper(self, location):
#             lat = float(location["lat"])
#             lng = float(location["lng"])
#
#             parking_id = (
#                 self.instance.id
#                 if hasattr(self, "instance") and self.instance
#                 else None
#             )
#
#             # Pobieramy punkty, ale pomijamy aktualny jeśli edycja
#             qs = ParkingPoint.objects.exclude(id=parking_id)
#
#             for point in qs:
#                 try:
#                     lat2 = float(point.location.get("lat"))
#                     lng2 = float(point.location.get("lng"))
#                 except Exception:
#                     # Pomijamy zepsute dane
#                     continue
#
#                 dist = haversine(lat, lng, lat2, lng2)
#
#                 if dist < distance_limit:
#                     raise ValidationError(
#                         f"Nowa lokalizacja znajduje się zbyt blisko istniejącego punktu ({dist:.2f} m < {distance_limit} m)."
#                     )
#
#             return func(self, location)
#
#         return wrapper
#
#     return decorator
