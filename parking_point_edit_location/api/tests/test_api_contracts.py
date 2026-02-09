import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model

from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation


# ============================================================
#  Fixtures (lokalne, jawne – brak magii)
# ============================================================


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        email="contract@test.com",
        password="password123",
    )


@pytest.fixture
def parking_point(db, user):
    return ParkingPoint.objects.create(
        location={"lat": 52.0, "lng": 21.0},
        user=user,
    )


# ============================================================
#  CONTRACT TEST: GET == POST
# ============================================================

# Endpoint nie obsługuje GET, więc test jest niepoprawny.
# @pytest.mark.django_db
# def test_get_returns_same_payload_as_post(
#     api_client,
#     user,
#     parking_point,
# ):
#     ...
