import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from Reviews.models import Review
from parking_point.models import ParkingPoint

User = get_user_model()


# -----------------------
# FIXTURES
# -----------------------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        password="password123",
        email="testemail@testuser.com",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser",
        password="password123",
        email="otheremail@otheruser.com",
    )


@pytest.fixture
def parking_point(db, user):
    return ParkingPoint.objects.create(
        user=user,
        location={"lat": 52.0, "lng": 21.0},
    )


# -----------------------
# TESTS
# -----------------------


@pytest.mark.django_db
def test_create_review(api_client, user, parking_point):
    """
    Pierwszy POST tworzy review
    """
    api_client.force_authenticate(user=user)
    url = f"/api/parking-points/{parking_point.id}/reviews/"

    payload = {
        "occupancy": "HIGH",
        "attributes": ["POOR_SURFACE"],
        "description": "Pierwsza opinia",
        "is_like": False,
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 201
    assert Review.objects.count() == 1

    review = Review.objects.get()
    assert review.user == user
    assert review.parking_point == parking_point
    assert review.occupancy == "HIGH"
    assert review.description == "Pierwsza opinia"


@pytest.mark.django_db
def test_second_post_updates_existing_review(api_client, user, parking_point):
    """
    Drugi POST nadpisuje istniejące review (UPSERT)
    """
    api_client.force_authenticate(user=user)
    url = f"/api/parking-points/{parking_point.id}/reviews/"

    api_client.post(
        url,
        {
            "occupancy": "LOW",
            "attributes": ["HARD_ACCESS"],
            "description": "Stara wersja",
            "is_like": False,
        },
        format="json",
    )

    api_client.post(
        url,
        {
            "occupancy": "HIGH",
            "attributes": ["POOR_LIGHTING"],
            "description": "Nowa wersja",
            "is_like": False,
        },
        format="json",
    )

    assert Review.objects.count() == 1

    review = Review.objects.get()
    assert review.occupancy == "HIGH"
    assert review.description == "Nowa wersja"
    assert review.attributes == ["POOR_LIGHTING"]


@pytest.mark.django_db
def test_different_users_can_review_same_parking_point(
    api_client, user, other_user, parking_point
):
    """
    Różni użytkownicy mogą dodać review do tego samego parking pointa
    """

    api_client.force_authenticate(user=user)
    url = f"/api/parking-points/{parking_point.id}/reviews/"
    api_client.post(
        url,
        {
            "occupancy": "LOW",
            "attributes": [],
            "description": "User 1",
            "is_like": False,
        },
        format="json",
    )

    api_client.force_authenticate(user=other_user)
    api_client.post(
        url,
        {
            "occupancy": "HIGH",
            "attributes": [],
            "description": "User 2",
            "is_like": False,
        },
        format="json",
    )

    assert Review.objects.count() == 2


@pytest.mark.django_db
def test_owner_review_sets_is_like_true(api_client, user, parking_point):
    """
    Właściciel parking pointa zawsze ma is_like=True
    """
    api_client.force_authenticate(user=user)
    url = f"/api/parking-points/{parking_point.id}/reviews/"
    api_client.post(
        url,
        {
            "occupancy": "MEDIUM",
            "attributes": [],
            "description": "Owner review",
            "is_like": False,  # frontend może wysłać False
        },
        format="json",
    )

    review = Review.objects.get()
    assert review.is_like is True


@pytest.mark.django_db
def test_list_reviews_for_parking_point(api_client, user, parking_point):
    """
    GET zwraca listę review dla parking pointa
    """
    api_client.force_authenticate(user=user)
    url = f"/api/parking-points/{parking_point.id}/reviews/"
    response = api_client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, list)


@pytest.mark.django_db
def test_authentication_required(api_client, parking_point):
    """
    Endpoint wymaga uwierzytelnienia
    """
    url = f"/api/parking-points/{parking_point.id}/reviews/"
    response = api_client.post(
        url,
        {
            "occupancy": "HIGH",
            "attributes": [],
            "description": "No auth",
            "is_like": False,
        },
        format="json",
    )

    assert response.status_code == 401
