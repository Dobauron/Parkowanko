import math
from rest_framework.exceptions import ValidationError
from ..models import ParkingPoint


def haversine(lat1, lng1, lat2, lng2):
    """
    Oblicza odległość Haversine między dwoma punktami geograficznymi w metrach.
    """
    R = 6371000  # Promień Ziemi w metrach
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def validate_proximity_to_existing_points(new_lat, new_lng, exclude_id=None):
    """
    Sprawdza, czy nowa lokalizacja znajduje się zbyt blisko istniejących punktów.
    """
    try:
        existing_points = (
            ParkingPoint.objects.exclude(id=exclude_id)
            if exclude_id
            else ParkingPoint.objects.all()
        )
    except Exception as e:
        raise ValidationError({"error":f"Błąd podczas pobierania istniejących punktów: {str(e)}"})

    for point in existing_points:
        try:
            existing_lat = float(point.location.get("lat", 0))
            existing_lng = float(point.location.get("lng", 0))
        except (KeyError, ValueError):
            raise ValidationError({"error":"Błąd w danych lokalizacji istniejących punktów."})

        distance = haversine(new_lat, new_lng, existing_lat, existing_lng)
        if distance < 40:  # Za blisko innego punktu
            raise ValidationError(
                {
                    "error": f"Nowa lokalizacja znajduje się zbyt blisko istniejącego punktu: {point.name} ({distance:.2f}m)."
                }
            )


def validate_distance_from_current_location(new_lat, new_lng, exclude_id, max_distance):
    """
    Sprawdza, czy nowa lokalizacja nie znajduje się zbyt daleko od obecnej pozycji.
    """
    if not isinstance(max_distance, (int, float)) or max_distance < 0:
        raise ValueError({"error":"Maksymalna odległość musi być dodatnią liczbą."})

    try:
        current_point = ParkingPoint.objects.get(id=exclude_id)
    except ParkingPoint.DoesNotExist:
        raise ValidationError({"error":f"Punkt parkingowy o ID {exclude_id} nie istnieje."})

    try:
        current_lat = float(current_point.location.get("lat", 0))
        current_lng = float(current_point.location.get("lng", 0))
    except (KeyError, ValueError):
        raise ValidationError({"error":"Błąd w danych lokalizacji obecnego punktu."})

    current_distance = haversine(new_lat, new_lng, current_lat, current_lng)
    if current_distance > max_distance:
        raise ValidationError(
            {"error":f"Nowa lokalizacja jest zbyt oddalona od obecnej pozycji: {current_distance:.2f}m (maksymalnie {max_distance}m)."}
        )


def validate_location(new_lat, new_lng, exclude_id=None, max_distance=None):
    """
    Walidacja lokalizacji punktu parkingowego:
    - Sprawdza, czy punkt znajduje się zbyt blisko innych punktów (100 m).
    - Opcjonalnie sprawdza, czy punkt nie jest zbyt daleko od swojej obecnej pozycji (max_distance).
    """

    # Sprawdzenie odległości do innych punktów
    validate_proximity_to_existing_points(new_lat, new_lng, exclude_id)

    # Sprawdzenie maksymalnej odległości (jeśli dotyczy)
    if max_distance is not None and exclude_id is not None:
        validate_distance_from_current_location(
            new_lat, new_lng, exclude_id, max_distance
        )
