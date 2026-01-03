import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from Reviews.api.serializers import ReviewSerializer
from Reviews.models import Review
from parking_point.models import ParkingPoint

User = get_user_model()


# -----------------------
# FIXTURES
# -----------------------


@pytest.fixture
def api_client_request_factory():
    return APIRequestFactory()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        password="password123",
        email="test@testuser.com",
    )


@pytest.fixture
def parking_point(db, user):
    return ParkingPoint.objects.create(
        user=user,
        location={"lat": 52.0, "lng": 21.0},
    )


@pytest.fixture
def api_request(api_client_request_factory, user):
    """
    Zwraca request DRF z user
    """
    req = api_client_request_factory.post("/")
    req.user = user
    return req


# -----------------------
# TESTS
# -----------------------


@pytest.mark.django_db
def test_serializer_creates_review(api_request, parking_point, user):
    """
    Serializer tworzy nowe review
    """
    data = {
        "occupancy": "HIGH",
        "attributes": ["POOR_SURFACE"],
        "description": "Testowa opinia",
        "is_like": False,
    }

    serializer = ReviewSerializer(
        data=data,
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    assert serializer.is_valid(), serializer.errors
    review = serializer.save()

    assert Review.objects.count() == 1
    assert review.user == user
    assert review.parking_point == parking_point
    assert review.occupancy == "HIGH"


@pytest.mark.django_db
def test_serializer_updates_existing_review(api_request, parking_point, user):
    """
    Drugi save() nadpisuje istniejące review (UPSERT)
    """
    Review.objects.create(
        user=user,
        parking_point=parking_point,
        occupancy="LOW",
        is_like=False,
    )

    data = {
        "occupancy": "HIGH",
        "attributes": ["POOR_LIGHTING"],
        "description": "Zmieniona opinia",
        "is_like": True,
    }

    serializer = ReviewSerializer(
        data=data,
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    assert serializer.is_valid(), serializer.errors
    review = serializer.save()

    assert Review.objects.count() == 1
    assert review.occupancy == "HIGH"
    assert review.attributes == ["POOR_LIGHTING"]
    assert review.description == "Zmieniona opinia"


@pytest.mark.django_db
def test_serializer_requires_occupancy(api_request, parking_point):
    """
    occupancy jest wymagane
    """
    serializer = ReviewSerializer(
        data={"description": "Brak occupancy"},
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    assert not serializer.is_valid()
    assert "occupancy" in serializer.errors


@pytest.mark.django_db
def test_serializer_rejects_invalid_occupancy(api_request, parking_point):
    """
    Niepoprawna wartość occupancy
    """
    serializer = ReviewSerializer(
        data={
            "occupancy": "INVALID",
            "is_like": False,
        },
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    assert not serializer.is_valid()
    assert "occupancy" in serializer.errors


@pytest.mark.django_db
def test_serializer_allows_empty_attributes(api_request, parking_point):
    """
    attributes mogą być puste
    """
    serializer = ReviewSerializer(
        data={
            "occupancy": "LOW",
            "attributes": [],
            "is_like": False,
        },
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    assert serializer.is_valid(), serializer.errors
    review = serializer.save()

    assert review.attributes == []


@pytest.mark.django_db
def test_serializer_sets_default_attributes_list(api_request, parking_point):
    """
    attributes domyślnie = []
    """
    serializer = ReviewSerializer(
        data={
            "occupancy": "LOW",
            "is_like": False,
        },
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    assert serializer.is_valid(), serializer.errors
    review = serializer.save()

    assert review.attributes == []


@pytest.mark.django_db
def test_serializer_user_is_read_only(api_request, parking_point):
    """
    user nie może być nadpisany w payloadzie
    """
    user = api_request.user
    other_user = User.objects.create_user(
        username="hacker",
        password="password123",
        email="hacker@localhost.com",
    )

    serializer = ReviewSerializer(
        data={
            "occupancy": "HIGH",
            "is_like": False,
            "user": other_user.id,
        },
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    assert serializer.is_valid(), serializer.errors
    review = serializer.save()

    assert review.user == user


@pytest.mark.django_db
def test_serializer_output_contains_user_data(api_request, parking_point):
    """
    get_user() zwraca id i username
    """
    serializer = ReviewSerializer(
        data={
            "occupancy": "MEDIUM",
            "is_like": False,
        },
        context={
            "request": api_request,
            "parking_point": parking_point,
        },
    )

    serializer.is_valid(raise_exception=True)
    review = serializer.save()

    output = ReviewSerializer(review).data
    assert output["user"]["id"] == api_request.user.id
    assert output["user"]["username"] == api_request.user.username
