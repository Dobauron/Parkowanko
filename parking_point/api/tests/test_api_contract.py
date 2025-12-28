import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from parking_point.models import ParkingPoint


# ============================================================
#  Fixtures
# ============================================================


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        email="pp_contract@test.com",
        password="password123",
    )


# ============================================================
#  CONTRACT TEST: GET == POST
# ============================================================


@pytest.mark.django_db
def test_parking_point_get_contains_post_payload(
    api_client,
    user,
):
    """
    POST -> tworzy ParkingPoint
    GET -> zwraca obiekt z IDENTYCZNYMI danymi
    """

    api_client.force_authenticate(user=user)

    url = "/api/parking-points/"

    payload = {"location": {"lat": 52.2297, "lng": 21.0122}}

    # -------- POST --------
    post_response = api_client.post(url, payload, format="json")

    assert post_response.status_code == status.HTTP_201_CREATED

    post_data = post_response.json()

    assert "id" in post_data
    assert post_data["location"] == payload["location"]

    created_id = post_data["id"]

    # -------- GET --------
    get_response = api_client.get(url)

    assert get_response.status_code == status.HTTP_200_OK

    data = get_response.json()

    # DRF może zwrócić listę albo paginated response
    results = data["results"] if "results" in data else data

    created_obj = next(item for item in results if item["id"] == created_id)

    # -------- CONTRACT ASSERTION --------
    assert created_obj == post_data
