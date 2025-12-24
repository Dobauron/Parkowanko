import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from parking_point.models import ParkingPoint
from parking_point_edit_location.models import (
    ParkingPointEditLocation,
    ParkingPointEditLocationVote,
)


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------
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
def edit_location(user_factory, parking_point):
    return ParkingPointEditLocation.objects.create(
        user=user_factory(),
        parking_point=parking_point,
        location={"lat": 52.1, "lng": 21.1},
    )


# ---------------------------------------------------------
# ParkingPointEditLocation tests
# ---------------------------------------------------------
@pytest.mark.django_db
def test_create_edit_location(edit_location):
    assert edit_location.pk is not None
    assert edit_location.like_count == 0
    assert edit_location.dislike_count == 0
    assert edit_location.created_at is not None
    assert edit_location.updated_at is not None


@pytest.mark.django_db
def test_edit_location_str(edit_location):
    text = str(edit_location)
    assert "want edit ParkingPoint id" in text
    assert str(edit_location.parking_point.id) in text


@pytest.mark.django_db
def test_edit_location_cascade_delete_user(edit_location):
    user = edit_location.user
    user.delete()

    assert ParkingPointEditLocation.objects.count() == 0


@pytest.mark.django_db
def test_edit_location_cascade_delete_parking_point(parking_point):
    parking_point.delete()

    assert ParkingPointEditLocation.objects.count() == 0


# ---------------------------------------------------------
# ParkingPointEditLocationVote tests
# ---------------------------------------------------------
@pytest.mark.django_db
def test_create_vote_like(user_factory, edit_location):
    vote = ParkingPointEditLocationVote.objects.create(
        parking_point_edit_location=edit_location,
        user=user_factory(),
        is_like=True,
    )

    assert vote.pk is not None
    assert vote.is_like is True
    assert vote.created_at is not None
    assert vote.updated_at is not None


@pytest.mark.django_db
def test_vote_str(user_factory, edit_location):
    vote = ParkingPointEditLocationVote.objects.create(
        parking_point_edit_location=edit_location,
        user=user_factory(),
        is_like=False,
    )

    assert str(vote.user) in str(vote)
    assert "voted for" in str(vote)


@pytest.mark.django_db
def test_unique_vote_per_user(edit_location, user_factory):
    user = user_factory()

    ParkingPointEditLocationVote.objects.create(
        parking_point_edit_location=edit_location,
        user=user,
        is_like=True,
    )

    with pytest.raises(IntegrityError):
        ParkingPointEditLocationVote.objects.create(
            parking_point_edit_location=edit_location,
            user=user,
            is_like=False,
        )


@pytest.mark.django_db
def test_vote_cascade_delete_edit_location(
    edit_location, user_factory
):
    ParkingPointEditLocationVote.objects.create(
        parking_point_edit_location=edit_location,
        user=user_factory(),
        is_like=True,
    )

    edit_location.delete()

    assert ParkingPointEditLocationVote.objects.count() == 0


@pytest.mark.django_db
def test_vote_cascade_delete_user(edit_location, user_factory):
    user = user_factory()

    ParkingPointEditLocationVote.objects.create(
        parking_point_edit_location=edit_location,
        user=user,
        is_like=True,
    )

    user.delete()

    assert ParkingPointEditLocationVote.objects.count() == 0
