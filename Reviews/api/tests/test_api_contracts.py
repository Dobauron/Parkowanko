import pytest
from rest_framework import status
from Reviews.models import Review
from Reviews.api.serializers import ReviewSerializer

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def user_factory(db, django_user_model):
    def make_user(username, email=None):
        if email is None:
            email = f"{username}@test.com"
        return django_user_model.objects.create_user(
            username=username, email=email, password="password"
        )

    return make_user


@pytest.fixture
def parking_point_factory(db):
    from parking_point.models import ParkingPoint

    def make_parking_point(user):
        return ParkingPoint.objects.create(
            location={"lat": 52.2297, "lng": 21.0122}, user=user
        )

    return make_parking_point


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


# ============================================================
# Testy kontraktów POST ↔ GET dla Review
# ============================================================


@pytest.mark.django_db
def test_review_post_get_consistency(user_factory, parking_point_factory, api_client):
    # Tworzymy użytkownika i punkt parkingowy
    user = user_factory("testuser_contract")
    pp = parking_point_factory(user=user)
    api_client.force_authenticate(user=user)

    # Dane do POST
    data = {
        "attributes": [],
        "occupancy": "LOW",
        "description": "Brak przekleństw",
        # Nie podajemy "is_like" – widok ustawi automatycznie, jeśli user jest właścicielem parking_point
    }

    # POST
    post_response = api_client.post(
        f"/api/parking-points/{pp.id}/reviews/",
        {
            "parking_point": pp.id,
            "attributes": [],
            "occupancy": "LOW",
            "description": "Brak przekleństw",
        },
        format="json",
    )
    assert post_response.status_code == status.HTTP_201_CREATED, post_response.data

    post_data = post_response.data

    # GET
    get_response = api_client.get(f"/api/parking-points/{pp.id}/reviews/")
    assert get_response.status_code == status.HTTP_200_OK, get_response.data

    get_data = get_response.data[0]

    # Porównanie danych: GET powinien zwrócić to samo co POST (po serializacji)
    for field in ["attributes", "occupancy", "description", "is_like"]:
        assert post_data[field] == get_data[field]
