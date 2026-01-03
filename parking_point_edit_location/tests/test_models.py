import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------
@pytest.fixture
def user_factory():
    User = get_user_model()
    counter = {"i": 0}

    def factory(**kwargs):
        counter["i"] += 1
        return User.objects.create_user(
            username=kwargs.get("username", f"user_{counter['i']}"),
            email=kwargs.get("email", f"user_{counter['i']}@test.pl"),
            password="password",
        )

    return factory


@pytest.fixture
def parking_point(user_factory):
    return ParkingPoint.objects.create(
        location={"lat": 52.0, "lng": 21.0},
        user=user_factory(),
    )


@pytest.fixture
def edit_location(user_factory, parking_point):
    return ParkingPointEditLocation.objects.create(
        user=user_factory(),
        parking_point=parking_point,
        location={"lat": 52.1, "lng": 21.1},
    )


# ---------------------------------------------------------
# ParkingPointEditLocation tests
# ---------------------------------------------------------
@pytest.mark.django_db
def test_create_edit_location(edit_location):
    assert edit_location.pk is not None
    assert edit_location.created_at is not None
    assert edit_location.updated_at is not None


@pytest.mark.django_db
def test_edit_location_cascade_delete_user(edit_location):
    user = edit_location.user
    user.delete()

    assert ParkingPointEditLocation.objects.count() == 0


@pytest.mark.django_db
def test_edit_location_cascade_delete_parking_point(parking_point):
    parking_point.delete()

    assert ParkingPointEditLocation.objects.count() == 0
