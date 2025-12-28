import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from parking_point.models import ParkingPoint
from Reviews.models import Review


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(
        email="testuser@gmail.com",
        password="password",
    )


@pytest.fixture
def parking_point(user):
    return ParkingPoint.objects.create(
        location={"lat": 52.2297, "lng": 21.0122},
        user=user,
    )


# ---------------------------------------------------------
# GET /api/parking-points/
# ---------------------------------------------------------
@pytest.mark.django_db
def test_get_parking_points_returns_list(api_client, parking_point):
    response = api_client.get("/api/parking-points/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_parking_points_contains_like_and_dislike_counts(api_client, parking_point):
    User = get_user_model()

    user_like = User.objects.create_user(
        username="user_like",
        email="like@gmail.com",
        password="password",
    )
    user_dislike = User.objects.create_user(
        username="user_dislike",
        email="dislike@gmail.com",
        password="password",
    )

    Review.objects.create(
        parking_point=parking_point,
        user=user_like,
        is_like=True,
    )
    Review.objects.create(
        parking_point=parking_point,
        user=user_dislike,
        is_like=False,
    )

    response = api_client.get("/api/parking-points/")

    assert response.status_code == status.HTTP_200_OK

    item = response.data[0]
    assert item["like_count"] == 1
    assert item["dislike_count"] == 1


# ---------------------------------------------------------
# POST /api/parking-points/
# ---------------------------------------------------------
@pytest.mark.django_db
def test_create_parking_point_authenticated_user(api_client, user):
    api_client.force_authenticate(user=user)

    data = {"location": {"lat": 52.2297, "lng": 21.0122}}
    response = api_client.post("/api/parking-points/", data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    assert "location" in response.data

    parking_point = ParkingPoint.objects.get(id=response.data["id"])
    assert parking_point.user == user


@pytest.mark.django_db
def test_create_parking_point_anonymous_user(api_client):
    data = {"location": {"lat": 52.2297, "lng": 21.0122}}
    response = api_client.post("/api/parking-points/", data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    parking_point = ParkingPoint.objects.get(id=response.data["id"])
    assert parking_point.user is None


@pytest.mark.django_db
def test_create_parking_point_invalid_location(api_client, user):
    api_client.force_authenticate(user=user)

    data = {"location": {"lat": "abc"}}
    response = api_client.post("/api/parking-points/", data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "location" in response.data


# ---------------------------------------------------------
# HTTP methods restrictions
# ---------------------------------------------------------
@pytest.mark.django_db
def test_put_is_not_allowed(api_client, parking_point):
    response = api_client.put(
        f"/api/parking-points/{parking_point.id}/",
        {"location": {"lat": 50.0, "lng": 20.0}},
        format="json",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_delete_is_not_allowed(api_client, parking_point):
    response = api_client.delete(f"/api/parking-points/{parking_point.id}/")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
