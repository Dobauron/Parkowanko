import pytest
from rest_framework.exceptions import ValidationError

from parking_point.models import ParkingPoint
from parking_point.api.validators import (
    haversine,
    reject_invalid_location_structure,
    reject_too_close_to_other_points,
)


# ---------------------------------------------------------
# Helper – Dummy serializer
# ---------------------------------------------------------
class DummySerializer:
    def __init__(self, instance=None):
        self.instance = instance

    @reject_invalid_location_structure
    def validate_location(self, location):
        return True

    @reject_invalid_location_structure
    @reject_too_close_to_other_points(distance_limit=50)
    def validate_location_with_distance(self, location):
        return True


# ---------------------------------------------------------
# Testy: haversine
# ---------------------------------------------------------
def test_haversine_zero_distance():
    assert haversine(10, 20, 10, 20) == 0


def test_haversine_known_distance():
    # Warszawa – Poznań ~279 km
    dist = haversine(52.2296756, 21.0122287, 52.406374, 16.9251681)
    assert 275_000 < dist < 300_000


# ---------------------------------------------------------
# Testy: reject_invalid_location_structure
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "invalid_location",
    ["not a dict", None, [], 123],
)
def test_location_must_be_dict(invalid_location):
    serializer = DummySerializer()

    with pytest.raises(ValidationError) as exc:
        serializer.validate_location(invalid_location)

    assert "musi być obiektem JSON" in str(exc.value)


@pytest.mark.parametrize(
    "invalid_location",
    [{"lat": 52}, {"lng": 21}, {}],
)
def test_location_missing_lat_or_lng(invalid_location):
    serializer = DummySerializer()

    with pytest.raises(ValidationError) as exc:
        serializer.validate_location(invalid_location)

    assert "musi zawierać klucze 'lat' i 'lng'" in str(exc.value)


@pytest.mark.parametrize(
    "invalid_location",
    [
        {"lat": "aaa", "lng": 21},
        {"lat": 52, "lng": None},
        {"lat": {}, "lng": []},
    ],
)
def test_location_lat_lng_must_be_numeric(invalid_location):
    serializer = DummySerializer()

    with pytest.raises(ValidationError) as exc:
        serializer.validate_location(invalid_location)

    assert "muszą być liczbami" in str(exc.value)


def test_location_allows_numeric_strings():
    serializer = DummySerializer()

    assert serializer.validate_location({"lat": "52.1", "lng": "21.0"}) is True


def test_valid_location_structure_passes():
    serializer = DummySerializer()

    assert serializer.validate_location({"lat": 52, "lng": 21}) is True


# ---------------------------------------------------------
# Testy: reject_too_close_to_other_points
# ---------------------------------------------------------
@pytest.mark.django_db
def test_reject_too_close_to_other_points_raises():
    ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})
    serializer = DummySerializer()

    with pytest.raises(ValidationError) as exc:
        serializer.validate_location_with_distance({"lat": 52.0001, "lng": 21.0001})

    assert "zbyt blisko istniejącego punktu" in str(exc.value)


@pytest.mark.django_db
def test_distance_equal_to_limit_is_allowed():
    ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})
    serializer = DummySerializer()

    # ~50 m różnicy
    assert (
        serializer.validate_location_with_distance(
            {"lat": 52.00045, "lng": 21.0}
        )
        is True
    )


@pytest.mark.django_db
def test_reject_too_close_allows_far_points():
    ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})
    serializer = DummySerializer()

    assert (
        serializer.validate_location_with_distance({"lat": 53.0, "lng": 22.0})
        is True
    )


@pytest.mark.django_db
def test_reject_too_close_ignores_self_when_editing():
    point = ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})
    serializer = DummySerializer(instance=point)

    assert (
        serializer.validate_location_with_distance({"lat": 52.0, "lng": 21.0})
        is True
    )


@pytest.mark.django_db
def test_instance_without_id_does_not_break():
    point = ParkingPoint(location={"lat": 52.0, "lng": 21.0})
    serializer = DummySerializer(instance=point)

    assert (
        serializer.validate_location_with_distance({"lat": 53.0, "lng": 22.0})
        is True
    )


@pytest.mark.django_db
def test_multiple_existing_points():
    ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})
    ParkingPoint.objects.create(location={"lat": 54.0, "lng": 23.0})
    serializer = DummySerializer()

    with pytest.raises(ValidationError):
        serializer.validate_location_with_distance({"lat": 52.0001, "lng": 21.0001})


@pytest.mark.django_db
def test_broken_location_data_in_db_is_ignored():
    ParkingPoint.objects.create(location={"lat": "abc", "lng": None})
    serializer = DummySerializer()

    assert (
        serializer.validate_location_with_distance({"lat": 50.0, "lng": 20.0})
        is True
    )


@pytest.mark.django_db
def test_invalid_structure_is_rejected_before_distance_check():
    ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0})
    serializer = DummySerializer()

    with pytest.raises(ValidationError) as exc:
        serializer.validate_location_with_distance({"lat": 52.0})

    assert "musi zawierać klucze" in str(exc.value)
