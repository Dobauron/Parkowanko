import pytest
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from parking_point_edit_location.api.validators import (
    validate_location_structure,
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
