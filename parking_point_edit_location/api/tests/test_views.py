import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------
@pytest.fixture
def api_client():
    return APIClient()


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
def proposal(user_factory, parking_point):
    return ParkingPointEditLocation.objects.create(
        user=user_factory(),
        parking_point=parking_point,
        location={"lat": 52.1, "lng": 21.1},
    )


# ---------------------------------------------------------
# ParkingPointEditLocationView
# ---------------------------------------------------------



@pytest.mark.django_db
def test_post_edit_location_requires_auth(api_client, parking_point):
    response = api_client.post(
        f"/api/parking-points/{parking_point.id}/edit-location/",
        {"location": {"lat": 50, "lng": 20}},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
