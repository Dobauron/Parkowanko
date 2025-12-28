import pytest
from rest_framework import serializers
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import (
    ParkingPointEditLocation,
    ParkingPointEditLocationVote,
)
from parking_point_edit_location.api.serializers import (
    ParkingPointEditLocationSerializer,
    ParkingPointEditLocationVoteSerializer,
)

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def user_factory(db, django_user_model):
    import uuid

    def create_user(email=None, username=None):
        if email is None:
            email = f"user_{uuid.uuid4().hex}@test.com"
        if username is None:
            username = f"user_{uuid.uuid4().hex}"
        return django_user_model.objects.create_user(
            email=email, username=username, password="password123"
        )

    return create_user


@pytest.fixture
def parking_point(user_factory):
    user = user_factory()
    return ParkingPoint.objects.create(
        location={"lat": 52.0, "lng": 21.0}, user=user, has_edit_location_proposal=False
    )


@pytest.fixture
def proposal(parking_point, user_factory):
    user = user_factory()
    return ParkingPointEditLocation.objects.create(
        user=user, parking_point=parking_point, location={"lat": 52.0005, "lng": 21.0}
    )


# ============================================================
# ParkingPointEditLocationSerializer
# ============================================================


@pytest.mark.django_db
def test_create_edit_location_serializer_ok(parking_point, user_factory):
    user = user_factory()
    data = {"location": {"lat": 52.0003, "lng": 21.0}}
    serializer = ParkingPointEditLocationSerializer(
        data=data, context={"parking_point": parking_point}
    )
    assert serializer.is_valid(), serializer.errors
    obj = serializer.save(user=user, parking_point=parking_point)
    assert obj.location == data["location"]


@pytest.mark.django_db
def test_create_edit_location_serializer_too_close(parking_point, user_factory):
    parking_point.has_edit_location_proposal = False
    parking_point.save()
    user = user_factory()
    data = {"location": {"lat": 52.0, "lng": 21.0}}  # odległość = 0
    serializer = ParkingPointEditLocationSerializer(
        data=data, context={"parking_point": parking_point}
    )
    assert not serializer.is_valid()
    assert "zbyt blisko" in str(serializer.errors.get("location", ""))


@pytest.mark.django_db
def test_like_dislike_counts(proposal, user_factory):
    users = [user_factory() for _ in range(3)]
    for i, u in enumerate(users):
        ParkingPointEditLocationVote.objects.create(
            user=u, parking_point_edit_location=proposal, is_like=(i < 2)
        )
    serializer = ParkingPointEditLocationSerializer(proposal)
    assert serializer.data["like_count"] == 2
    assert serializer.data["dislike_count"] == 1


# ============================================================
# ParkingPointEditLocationVoteSerializer
# ============================================================


@pytest.mark.django_db
def test_vote_serializer_ok(proposal, user_factory):
    user = user_factory()
    data = {"is_like": True}
    serializer = ParkingPointEditLocationVoteSerializer(
        data=data,
        context={
            "proposal": proposal,
            "request": type("Req", (), {"user": user, "method": "POST"})(),
            "method": "POST",
        },
    )
    assert serializer.is_valid(), serializer.errors
    obj = serializer.save(user=user, parking_point_edit_location=proposal)
    assert obj.is_like is True


@pytest.mark.django_db
def test_vote_serializer_already_voted(proposal, user_factory):
    user = user_factory()
    ParkingPointEditLocationVote.objects.create(
        user=user, parking_point_edit_location=proposal, is_like=True
    )
    data = {"is_like": False}
    serializer = ParkingPointEditLocationVoteSerializer(
        data=data,
        context={
            "proposal": proposal,
            "request": type("Req", (), {"user": user, "method": "POST"})(),
            "method": "POST",
        },
    )
    assert not serializer.is_valid()
    assert "Już oddałeś głos" in str(serializer.errors)


@pytest.mark.django_db
def test_vote_serializer_invalid_is_like(proposal, user_factory):
    user = user_factory()
    data = {"is_like": "abc"}
    serializer = ParkingPointEditLocationVoteSerializer(
        data=data,
        context={
            "proposal": proposal,
            "request": type("Req", (), {"user": user, "method": "POST"})(),
            "method": "POST",
        },
    )
    assert not serializer.is_valid()
    assert "Must be a valid boolean." in str(serializer.errors["is_like"][0])
