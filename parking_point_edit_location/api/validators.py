from rest_framework import serializers
from django.core.exceptions import ValidationError
from ..models import ParkingPointEditLocation
from parking_point.api.validators import haversine


def get_distance_between_locations(new_loc, current_loc):
    """
    Oblicza odległość między dwoma lokalizacjami
    Zwraca: (distance_in_meters, error_message_or_None)
    """
    try:
        new_lat = float(new_loc["lat"])
        new_lng = float(new_loc["lng"])
        current_lat = float(current_loc["lat"])
        current_lng = float(current_loc["lng"])

        distance = haversine(new_lat, new_lng, current_lat, current_lng)
        return distance, None

    except KeyError:
        return None, "Brak wymaganych pól lat/lng w lokalizacji"
    except (ValueError, TypeError):
        return None, "Nieprawidłowy format współrzędnych"


# ----- DEKORATORY WALIDACYJNE -----
def validate_location_structure():
    """
    Waliduje czy location ma poprawną strukturę JSON z lat i lng
    """

    def decorator(validate_method):
        def wrapper(self, attrs):
            location = attrs.get("location")

            if not location:
                raise serializers.ValidationError(
                    {"location": "Pole location jest wymagane."}
                )

            if not isinstance(location, dict):
                raise serializers.ValidationError(
                    {"location": "Location musi być obiektem JSON."}
                )

            if "lat" not in location or "lng" not in location:
                raise serializers.ValidationError(
                    {"location": "Location musi zawierać lat i lng."}
                )

            try:
                lat = float(location["lat"])
                lng = float(location["lng"])

                if not (-90 <= lat <= 90):
                    raise serializers.ValidationError(
                        {
                            "location": "Szerokość geograficzna (lat) musi być między -90 a 90."
                        }
                    )

                if not (-180 <= lng <= 180):
                    raise serializers.ValidationError(
                        {
                            "location": "Długość geograficzna (lng) musi być między -180 a 180."
                        }
                    )

            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    {"location": "Pola lat i lng muszą być liczbami."}
                )

            return validate_method(self, attrs)

        return wrapper

    return decorator


def validate_distance(min_distance=20, max_distance=100):
    """
    JEDEN walidator który sprawdza zakres odległości 20-100 metrów
    """

    def decorator(validate_method):
        def wrapper(self, attrs):
            location = attrs.get("location")
            parking_point = self.context.get("parking_point")

            if location and parking_point:
                current_location = parking_point.location

                # Sprawdź czy obecna lokalizacja istnieje
                if (
                    not current_location
                    or "lat" not in current_location
                    or "lng" not in current_location
                ):
                    raise serializers.ValidationError(
                        {
                            "location": "Obecna lokalizacja punktu nie zawiera poprawnych współrzędnych."
                        }
                    )

                # Oblicz odległość
                distance, error = get_distance_between_locations(
                    location, current_location
                )

                if error:
                    raise serializers.ValidationError({"location": error})

                # JEDNA walidacja z zakresem
                if distance < min_distance:
                    raise serializers.ValidationError(
                        {
                            "location": f"Nowa lokalizacja jest zbyt blisko obecnej. "
                            f"Odległość: {distance:.1f}m, minimalnie: {min_distance}m."
                        }
                    )

                if distance > max_distance:
                    raise serializers.ValidationError(
                        {
                            "location": f"Nowa lokalizacja jest zbyt daleko od obecnej. "
                            f"Odległość: {distance:.1f}m, maksymalnie: {max_distance}m."
                        }
                    )

            return validate_method(self, attrs)

        return wrapper

    return decorator
