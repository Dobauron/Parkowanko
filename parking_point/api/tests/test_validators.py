import pytest
from rest_framework.exceptions import ValidationError
from parking_point.api.validators import (
    haversine,
    validate_proximity_to_existing_points,
    validate_distance_from_current_location,
    validate_location,
)
from parking_point.models import ParkingPoint
from django.contrib import get_user_model


@pytest.mark.parametrize(
    "lat1, lng1, lat2, lng2, expected_distance",
    [
        (52.2297, 21.0122, 52.2297, 21.0122, 0),  # Ten sam punkt
        (52.2297, 21.0122, 52.4064, 16.9252, 278545),  # Warszawa -> Poznań
        (52.2297, 21.0122, 50.0614, 19.9383, 252289),  # Warszawa -> Kraków
    ],
)
def test_haversine(lat1, lng1, lat2, lng2, expected_distance):
    """Testuje funkcję Haversine dla różnych odległości"""
    distance = haversine(lat1, lng1, lat2, lng2)
    assert pytest.approx(distance, rel=0.01) == expected_distance  # Tolerancja 1%


@pytest.mark.django_db
def test_validate_proximity_to_existing_points():
    """Testuje walidację bliskości lokalizacji"""
    user = get_user_model().objects.create_user(
        email="test@example.com", password="testpass"
    )

    ParkingPoint.objects.create(
        name="Existing Point",
        location={"lat": 52.2297, "lng": 21.0122},
        user=user,
    )

    # Próba dodania punktu w tej samej lokalizacji (powinna zwrócić błąd)
    with pytest.raises(
        ValidationError,
        match="Nowa lokalizacja znajduje się zbyt blisko istniejącego punktu",
    ):
        validate_proximity_to_existing_points(52.2297, 21.0122)


@pytest.mark.django_db
def test_validate_distance_from_current_location():
    """Testuje walidację maksymalnej odległości od istniejącego punktu"""
    user = get_user_model().objects.create_user(
        email="test@example.com", password="testpass"
    )

    parking_point = ParkingPoint.objects.create(
        name="Current Point",
        location={"lat": 52.2297, "lng": 21.0122},
        user=user,
    )

    # Próba aktualizacji do punktu w odległości 500m (powinna przejść)
    validate_distance_from_current_location(52.2301, 21.0125, parking_point.id, 1000)

    # Próba aktualizacji do punktu w odległości 2km (powinna zgłosić błąd)
    with pytest.raises(ValidationError, match="Nowa lokalizacja jest zbyt oddalona"):
        validate_distance_from_current_location(52.245, 21.025, parking_point.id, 1000)


@pytest.mark.django_db
def test_validate_location():
    """Testuje walidację lokalizacji"""
    user = get_user_model().objects.create_user(
        email="test@example.com", password="testpass"
    )

    parking_point = ParkingPoint.objects.create(
        name="Existing Point",
        location={"lat": 52.2297, "lng": 21.0122},
        user=user,
    )

    # Próba dodania nowego punktu w bliskiej odległości (powinna zgłosić błąd)
    with pytest.raises(
        ValidationError,
        match="Nowa lokalizacja znajduje się zbyt blisko istniejącego punktu",
    ):
        validate_location(52.2298, 21.0123)

    # Próba aktualizacji punktu na dużą odległość (powinna zgłosić błąd)
    with pytest.raises(ValidationError, match="Nowa lokalizacja jest zbyt oddalona"):
        validate_location(52.245, 21.025, parking_point.id, 1000)
