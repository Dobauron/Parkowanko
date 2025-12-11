import pytest
from rest_framework.exceptions import ValidationError

from ..validators import (
    haversine,
    reject_invalid_location_structure,
    reject_too_close_to_other_points,
)

from parking_point.models import ParkingPoint



# ---------------------------------------------------------
# Test: haversine
# ---------------------------------------------------------
def test_haversine_zero_distance():
    assert haversine(10, 20, 10, 20) == 0


def test_haversine_known_distance():
    # Przybliżona odległość między punktami
    dist = haversine(52.2296756, 21.0122287, 52.406374, 16.9251681)
    assert 275000 < dist < 300000  # ~279 km


# ---------------------------------------------------------
# Helper do tworzenia sztucznej walidowanej klasy
# ---------------------------------------------------------
class DummySerializer:
    def __init__(self, instance=None):
        self.instance = instance


# ---------------------------------------------------------
# Testy: reject_invalid_location_structure
# ---------------------------------------------------------
def test_invalid_location_not_dict():
    @reject_invalid_location_structure
    def dummy(self, location):
        return True

    with pytest.raises(ValidationError):
        dummy(DummySerializer(), "not a dict")


def test_invalid_location_missing_keys():
    @reject_invalid_location_structure
    def dummy(self, location):
        return True

    with pytest.raises(ValidationError):
        dummy(DummySerializer(), {"lat": 10})


def test_invalid_location_non_numeric_values():
    @reject_invalid_location_structure
    def dummy(self, location):
        return True

    with pytest.raises(ValidationError):
        dummy(DummySerializer(), {"lat": "aaa", "lng": 52})


def test_valid_location_structure():
    @reject_invalid_location_structure
    def dummy(self, location):
        return True

    assert dummy(DummySerializer(), {"lat": 52, "lng": 21}) is True


# ---------------------------------------------------------
# Testy: reject_too_close_to_other_points
# ---------------------------------------------------------
@pytest.mark.django_db
def test_reject_too_close_to_other_points_raises():
    # Mamy istniejący punkt
    ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})

    @reject_too_close_to_other_points(distance_limit=50)
    def dummy(self, location):
        return True

    with pytest.raises(ValidationError):
        dummy(DummySerializer(), {"lat": 52.0001, "lng": 21.0001})  # bardzo blisko


@pytest.mark.django_db
def test_reject_too_close_to_other_points_allows_far_points():
    ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})

    @reject_too_close_to_other_points(distance_limit=50)
    def dummy(self, location):
        return True

    assert dummy(DummySerializer(), {"lat": 53.0, "lng": 22.0}) is True


@pytest.mark.django_db
def test_reject_too_close_ignores_self_when_editing():
    # Punkt istniejący
    point = ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})

    @reject_too_close_to_other_points(distance_limit=50)
    def dummy(self, location):
        return True

    # Podczas edycji walidator nie sprawdza punktu przeciwko sobie
    serializer = DummySerializer(instance=point)

    assert dummy(serializer, {"lat": 52.0, "lng": 21.0}) is True
