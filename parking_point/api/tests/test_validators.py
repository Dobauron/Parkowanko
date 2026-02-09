import pytest
from rest_framework.exceptions import ValidationError

from parking_point.models import ParkingPoint
from parking_point.api.validators import reject_invalid_location_structure
from parking_point.utils.geo_utils import haversine


# ---------------------------------------------------------
# Helper – Dummy serializer
# ---------------------------------------------------------
class DummySerializer:
    def __init__(self, instance=None):
        self.instance = instance

    @reject_invalid_location_structure
    def validate_location(self, location):
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
