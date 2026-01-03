import pytest
from rest_framework import serializers
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation
from parking_point_edit_location.api.serializers import ParkingPointEditLocationSerializer

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def user_factory(db, django_user_model):
    import uuid

    def create_user(email=None, username=None):
        if email is None:
            email = f"user_{uuid.uuid4().hex}@test.com"
        if username is None:
            username = f"user_{uuid.uuid4().hex}"
        return django_user_model.objects.create_user(
            email=email, username=username, password="password123"
        )

    return create_user


@pytest.fixture
def parking_point(user_factory):
    user = user_factory()
    return ParkingPoint.objects.create(
        location={"lat": 52.0, "lng": 21.0}, user=user
    )


@pytest.fixture
def proposal(parking_point, user_factory):
    user = user_factory()
    return ParkingPointEditLocation.objects.create(
        user=user, parking_point=parking_point, location={"lat": 52.0005, "lng": 21.0}
    )


# ============================================================
# ParkingPointEditLocationSerializer
# ============================================================


@pytest.mark.django_db
def test_create_edit_location_serializer_ok(parking_point, user_factory):
    user = user_factory()
    data = {"location": {"lat": 52.0003, "lng": 21.0}}
    serializer = ParkingPointEditLocationSerializer(
        data=data, context={"parking_point": parking_point}
    )
    assert serializer.is_valid(), serializer.errors
    obj = serializer.save(user=user, parking_point=parking_point)
    assert obj.location == data["location"]


@pytest.mark.django_db
def test_create_edit_location_serializer_too_close(parking_point, user_factory):
    parking_point.save()
    user = user_factory()
    data = {"location": {"lat": 52.0, "lng": 21.0}}  # odległość = 0
    serializer = ParkingPointEditLocationSerializer(
        data=data, context={"parking_point": parking_point}
    )
    assert not serializer.is_valid()
    assert "zbyt blisko" in str(serializer.errors.get("location", ""))


