import pytest
from django.contrib.auth import get_user_model

from parking_point.api.serializers import ParkingPointSerializer
from parking_point.models import ParkingPoint

User = get_user_model()


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------
@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="testpass",
    )


@pytest.fixture
def fake_request(user):
    """
    Minimalny obiekt request wymagany przez
    serializers.CurrentUserDefault()
    """
    return type("Request", (), {"user": user})()


@pytest.fixture
def valid_location():
    return {"lat": 52.2297, "lng": 21.0122}


# ---------------------------------------------------------
# Testy POST – walidacja danych
# ---------------------------------------------------------
@pytest.mark.django_db
class TestParkingPointSerializerPost:
    def test_valid_serialization(self, fake_request, valid_location):
        serializer = ParkingPointSerializer(
            data={"location": valid_location},
            context={"request": fake_request},
        )

        assert serializer.is_valid(), serializer.errors

        instance = serializer.save()
        assert instance.location == valid_location
        assert instance.user == fake_request.user

    def test_missing_location_field(self, fake_request):
        serializer = ParkingPointSerializer(
            data={},
            context={"request": fake_request},
        )

        assert not serializer.is_valid()
        assert "location" in serializer.errors

    def test_invalid_location_format(self, fake_request):
        serializer = ParkingPointSerializer(
            data={"location": {"lat": "invalid", "lng": "invalid"}},
            context={"request": fake_request},
        )

        assert not serializer.is_valid()
        assert "location" in serializer.errors

    def test_location_none(self, fake_request):
        serializer = ParkingPointSerializer(
            data={"location": None},
            context={"request": fake_request},
        )

        assert not serializer.is_valid()
        assert "location" in serializer.errors

    def test_location_too_close(self, fake_request, valid_location):
        ParkingPoint.objects.create(
            location=valid_location,
            user=fake_request.user,
        )

        serializer = ParkingPointSerializer(
            data={"location": valid_location},
            context={"request": fake_request},
        )

        assert not serializer.is_valid()
        assert "location" in serializer.errors
        assert "zbyt blisko" in str(serializer.errors["location"][0])


# ---------------------------------------------------------
# Testy GET – serializacja obiektu
# ---------------------------------------------------------
@pytest.mark.django_db
class TestParkingPointSerializerGet:
    def test_get_serialization(self, user, valid_location):
        point = ParkingPoint.objects.create(
            location=valid_location,
            user=user,
        )

        serializer = ParkingPointSerializer(point)
        data = serializer.data

        assert data["id"] == point.id
        assert data["location"] == valid_location
        assert data["like_count"] == 0
        assert data["dislike_count"] == 0
