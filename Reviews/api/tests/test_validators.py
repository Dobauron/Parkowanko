import pytest
from rest_framework.exceptions import ValidationError
from Reviews.api.validators import (
    validate_attributes,
    validate_occupancy,
    validate_no_profanity,
    validate_unique_review,
)
from Reviews.models import Review
from parking_point.models import ParkingPoint


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def user_factory(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    created_users = []

    def make_user(username):
        user = User.objects.create_user(
            username=username, email=f"{username}@test.com", password="pass"
        )
        created_users.append(user)
        return user

    return make_user


@pytest.fixture
def parking_point_factory(user_factory, db):
    points = []

    def make_parking_point(user=None, lat=52.0, lng=21.0):
        if user is None:
            user = user_factory("owner")
        pp = ParkingPoint.objects.create(location={"lat": lat, "lng": lng}, user=user)
        points.append(pp)
        return pp

    return make_parking_point


# ============================================================
# validate_attributes
# ============================================================


def test_validate_attributes_valid():
    for choice in [c[0] for c in Review.Attributes.choices]:
        assert validate_attributes(choice) == choice


def test_validate_attributes_invalid():
    with pytest.raises(ValidationError):
        validate_attributes("INVALID")


# ============================================================
# validate_occupancy
# ============================================================


def test_validate_occupancy_valid():
    for choice in [c[0] for c in Review.Occupancy.choices]:
        assert validate_occupancy(choice) == choice


def test_validate_occupancy_invalid():
    with pytest.raises(ValidationError):
        validate_occupancy("INVALID")


# ============================================================
# validate_no_profanity
# ============================================================


def test_validate_no_profanity_clean_text():
    text = "To jest poprawny opis."
    assert validate_no_profanity(text) == text


@pytest.mark.parametrize("bad_word", ["kurwa", "chuj", "pizda"])
def test_validate_no_profanity_blocked_text(bad_word):
    with pytest.raises(ValidationError):
        validate_no_profanity(f"To zawiera {bad_word}")


# ============================================================
# validate_unique_review
# ============================================================


@pytest.mark.django_db
def test_validate_unique_review_allows_new_review(user_factory, parking_point_factory):
    user = user_factory("user1")
    pp = parking_point_factory(user=user)

    class DummySerializer:
        context = {"request": type("Request", (), {"user": user})()}
        instance = None

    serializer = DummySerializer()
    attrs = {"parking_point": pp}

    # Funkcja dummy musi przyjmować dwa argumenty: self, attrs
    def dummy_validate(self, attrs):
        return attrs

    wrapper = validate_unique_review(dummy_validate)
    assert wrapper(serializer, attrs) == attrs


@pytest.mark.django_db
def test_validate_unique_review_blocks_duplicate(user_factory, parking_point_factory):
    user = user_factory("user2")
    pp = parking_point_factory(user=user)

    Review.objects.create(
        user=user, parking_point=pp, occupancy=Review.Occupancy.HIGH, is_like=True
    )

    class DummySerializer:
        context = {"request": type("Request", (), {"user": user})()}
        instance = None

    serializer = DummySerializer()
    attrs = {"parking_point": pp}

    def dummy_validate(self, attrs):
        return attrs

    wrapper = validate_unique_review(dummy_validate)
    import pytest

    with pytest.raises(ValidationError):
        wrapper(serializer, attrs)
