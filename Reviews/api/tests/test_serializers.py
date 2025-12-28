import pytest
from django.contrib.auth import get_user_model
from parking_point.models import ParkingPoint
from Reviews.models import Review
from Reviews.api.serializers import ReviewSerializer

User = get_user_model()


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def user_factory(db):
    """
    Fabryka użytkowników. Zwraca funkcję do tworzenia wielu użytkowników
    """
    created_users = []

    def make_user(username, email=None):
        nonlocal created_users
        email = email or f"{username}@test.com"
        user = User.objects.create_user(username=username, email=email, password="pass")
        created_users.append(user)
        return user

    return make_user


@pytest.fixture
def parking_point_factory(user_factory, db):
    """
    Fabryka ParkingPoint. Zwraca funkcję do tworzenia punktów.
    """
    points = []

    def make_parking_point(user=None, lat=52.0, lng=21.0):
        nonlocal points
        if user is None:
            user = user_factory("owner")
        pp = ParkingPoint.objects.create(location={"lat": lat, "lng": lng}, user=user)
        points.append(pp)
        return pp

    return make_parking_point


# ============================================================
# Testy serializera
# ============================================================

@pytest.mark.django_db
def test_review_serializer_valid(user_factory, parking_point_factory):
    user = user_factory("testuser1")
    pp = parking_point_factory(user=user)

    data = {
        "attributes": [],
        "occupancy": Review.Occupancy.LOW,
        "description": "Bez przekleństw",
        "is_like": True,
    }

    request = type("Request", (), {"user": user})()  # prosty dummy request

    serializer = ReviewSerializer(
        data=data,
        context={"request": request, "parking_point": pp}
    )

    assert serializer.is_valid(), serializer.errors
    review = serializer.save(user=user, parking_point=pp)
    assert review.pk is not None

@pytest.mark.django_db
def test_review_serializer_invalid_occupancy(user_factory, parking_point_factory):
    user = user_factory("user2")
    pp = parking_point_factory(user=user)
    data = {"occupancy": "INVALID_OCCUPANCY", "is_like": True}
    serializer = ReviewSerializer(data=data, context={"user": user, "parking_point": pp})
    assert not serializer.is_valid()
    assert "occupancy" in serializer.errors

@pytest.mark.django_db
def test_review_serializer_description_profanity(user_factory, parking_point_factory):
    user = user_factory("testuser1")
    pp = parking_point_factory(user=user)

    data = {
        "attributes": [],
        "occupancy": Review.Occupancy.LOW,
        "description": "kurwa",
        "is_like": True,
    }

    request = type("Request", (), {"user": user})()
    serializer = ReviewSerializer(data=data, context={"request": request, "parking_point": pp})

    assert not serializer.is_valid()
    assert "Opis zawiera niedozwolone słowa" in str(serializer.errors)

@pytest.mark.django_db
def test_review_serializer_unique_review(user_factory, parking_point_factory):
    user = user_factory("testuser23")
    pp = parking_point_factory(user=user)

    Review.objects.create(user=user, parking_point=pp, occupancy=Review.Occupancy.LOW, is_like=True)

    data = {
        "attributes": [],
        "occupancy": Review.Occupancy.LOW,
        "description": "Brak przekleństw",
        "is_like": True,
    }

    request = type("Request", (), {"user": user})()
    serializer = ReviewSerializer(data=data, context={"request": request, "parking_point": pp})

    assert not serializer.is_valid()
    assert "Możesz dodać tylko jedną recenzję" in str(serializer.errors)

@pytest.mark.django_db
def test_review_serializer_get_user_field(user_factory, parking_point_factory):
    user = user_factory("user5")
    pp = parking_point_factory(user=user)
    review = Review.objects.create(user=user, parking_point=pp, occupancy=Review.Occupancy.MEDIUM, is_like=True)
    serializer = ReviewSerializer(instance=review)
    user_data = serializer.data["user"]
    assert user_data["id"] == user.id
    assert user_data["username"] == user.username
