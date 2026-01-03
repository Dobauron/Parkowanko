import pytest
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from parking_point_edit_location.api.validators import (
    validate_location_structure,
    validate_distance,
)
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


# ============================================================
#  Fixtures
# ============================================================


@pytest.fixture
def user_factory(db):
    def create_user(email=None, username=None):
        if email is None:
            email = f"user_{uuid.uuid4().hex}@test.com"
        if username is None:
            username = f"user_{uuid.uuid4().hex}"
        return User.objects.create_user(
            email=email, username=username, password="password123"
        )

    return create_user


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def parking_point(db, user_factory):
    user = user_factory()
    return ParkingPoint.objects.create(
        location={"lat": 52.0, "lng": 21.0},
        user=user,
    )


@pytest.fixture
def edit_location(db, user_factory, parking_point):
    user = user_factory()
    return ParkingPointEditLocation.objects.create(
        user=user,
        parking_point=parking_point,
        location={"lat": 52.0003, "lng": 21.0},
    )


# ============================================================
#  Helpers
# ============================================================


class DummySerializer(serializers.Serializer):
    location = serializers.JSONField(required=False)

    def validate(self, attrs):
        return attrs


# ============================================================
#  validate_location_structure
# ============================================================


def test_validate_location_structure_valid():
    class TestSerializer(DummySerializer):
        @validate_location_structure()
        def validate(self, attrs):
            return attrs

    serializer = TestSerializer(data={"location": {"lat": 52.1, "lng": 21.0}})

    assert serializer.is_valid(), serializer.errors


@pytest.mark.parametrize(
    "location",
    [
        None,
        {},
        {"lat": 10},
        {"lng": 10},
        {"lat": "abc", "lng": 10},
        {"lat": 1000, "lng": 10},
        {"lat": 10, "lng": 1000},
    ],
)
def test_validate_location_structure_invalid(location):
    class TestSerializer(DummySerializer):
        @validate_location_structure()
        def validate(self, attrs):
            return attrs

    serializer = TestSerializer(data={"location": location})
    assert not serializer.is_valid()
    assert "location" in serializer.errors

# ============================================================
#  validate_distance
# ============================================================


@pytest.mark.django_db
def test_validate_distance_ok(parking_point):
    parking_point.location = {"lat": 52.0, "lng": 21.0}
    parking_point.save()

    class TestSerializer(DummySerializer):
        @validate_distance(min_distance=20, max_distance=100)
        def validate(self, attrs):
            return attrs

    serializer = TestSerializer(
        data={"location": {"lat": 52.0003, "lng": 21.0}},  # ~33m
        context={"parking_point": parking_point},
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_validate_distance_too_close(parking_point):
    parking_point.location = {"lat": 52.0, "lng": 21.0}
    parking_point.save()

    class TestSerializer(DummySerializer):
        @validate_distance()
        def validate(self, attrs):
            return attrs

    serializer = TestSerializer(
        data={"location": {"lat": 52.00005, "lng": 21.0}},  # ~5m
        context={"parking_point": parking_point},
    )

    assert not serializer.is_valid()
    assert "zbyt blisko" in serializer.errors["location"][0]


@pytest.mark.django_db
def test_validate_distance_too_far(parking_point):
    parking_point.location = {"lat": 52.0, "lng": 21.0}
    parking_point.save()

    class TestSerializer(DummySerializer):
        @validate_distance()
        def validate(self, attrs):
            return attrs

    serializer = TestSerializer(
        data={"location": {"lat": 52.002, "lng": 21.0}},  # ~220m
        context={"parking_point": parking_point},
    )

    assert not serializer.is_valid()
    assert "zbyt daleko" in serializer.errors["location"][0]


