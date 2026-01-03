import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from parking_point.models import ParkingPoint
from Reviews.models import Review

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="user1", email="user1@test.com", password="pass"
    )


@pytest.fixture
def owner_user():
    return User.objects.create_user(
        username="owner", email="owner@test.com", password="pass"
    )


@pytest.fixture
def parking_point(owner_user):
    return ParkingPoint.objects.create(
        location={"lat": 52.0, "lng": 21.0}, user=owner_user
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_get_reviews_empty(api_client, parking_point, user):
    api_client.force_authenticate(user=user)
    response = api_client.get(f"/api/parking-points/{parking_point.id}/reviews/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_post_review_creates(api_client, parking_point, user):
    api_client.force_authenticate(user=user)
    data = {
        "occupancy": Review.Occupancy.HIGH,
        "is_like": False,
        "attributes": [Review.Attributes.POOR_SURFACE],
        "description": "Dobra lokalizacja",
    }
    response = api_client.post(
        f"/api/parking-points/{parking_point.id}/reviews/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.filter(parking_point=parking_point, user=user).exists()
    review = Review.objects.get(parking_point=parking_point, user=user)
    assert review.occupancy == Review.Occupancy.HIGH


@pytest.mark.django_db
def test_post_review_owner_sets_is_like(api_client, parking_point, owner_user):
    api_client.force_authenticate(user=owner_user)
    data = {
        "occupancy": Review.Occupancy.MEDIUM,
        "attributes": [Review.Attributes.FLOOD_PRONE],
        "description": "Test dla właściciela",
    }
    response = api_client.post(
        f"/api/parking-points/{parking_point.id}/reviews/", data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    review = Review.objects.get(parking_point=parking_point, user=owner_user)
    # is_like automatycznie ustawione na True
    assert review.is_like is True


@pytest.mark.django_db
def test_post_duplicate_review_returns_error(api_client, parking_point, user):
    api_client.force_authenticate(user=user)
    Review.objects.create(
        parking_point=parking_point,
        user=user,
        occupancy=Review.Occupancy.HIGH,
        is_like=True,
    )
    data = {"occupancy": Review.Occupancy.LOW, "is_like": False}
    response = api_client.post(
        f"/api/parking-points/{parking_point.id}/reviews/", data, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Możesz dodać tylko jedną recenzję dla tego parking point." in str(
        response.data
    )
