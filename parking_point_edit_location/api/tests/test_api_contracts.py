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

@pytest.mark.django_db
def test_get_returns_same_payload_as_post(
    api_client,
    user,
    parking_point,
):
    api_client.force_authenticate(user=user)

    url = f"/api/parking-points/{parking_point.id}/edit-location/"

    payload = {
        "location": {
            "lat": parking_point.location["lat"] + 0.0003,
            "lng": parking_point.location["lng"],
        }
    }

    # -------- POST --------
    post_response = api_client.post(url, payload, format="json")

    assert post_response.status_code == status.HTTP_201_CREATED

    post_data = post_response.json()

    assert "id" in post_data
    assert post_data["location"] == payload["location"]

    # -------- GET --------
    get_response = api_client.get(url)

    assert get_response.status_code == status.HTTP_200_OK

    get_data = get_response.json()

    # -------- CONTRACT ASSERTION --------
    assert get_data == post_data
