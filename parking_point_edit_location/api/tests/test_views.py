import pytest
from rest_framework import status
from rest_framework.test import APIClient
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
def api_client():
    return APIClient()


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
def proposal(user_factory, parking_point):
    return ParkingPointEditLocation.objects.create(
        user=user_factory(),
        parking_point=parking_point,
        location={"lat": 52.1, "lng": 21.1},
    )


# ---------------------------------------------------------
# ParkingPointEditLocationView
# ---------------------------------------------------------
@pytest.mark.django_db
def test_get_edit_location_returns_404_when_missing(api_client, user_factory, parking_point):
    user = user_factory()
    api_client.force_authenticate(user=user)

    response = api_client.get(
        f"/api/parking-points/{parking_point.id}/edit-location/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_edit_location_returns_existing_proposal(
    api_client, user_factory, proposal
):
    user = user_factory()
    api_client.force_authenticate(user=user)

    response = api_client.get(
        f"/api/parking-points/{proposal.parking_point.id}/edit-location/"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["location"] == proposal.location


@pytest.mark.django_db
def test_post_edit_location_creates_proposal_and_initial_vote(
    api_client, user_factory, parking_point
):
    user = user_factory()
    api_client.force_authenticate(user=user)

    # ~33 metry od oryginalnej lokalizacji
    data = {
        "location": {
            "lat": parking_point.location["lat"] + 0.0003,
            "lng": parking_point.location["lng"],
        }
    }

    response = api_client.post(
        f"/api/parking-points/{parking_point.id}/edit-location/",
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    proposal = ParkingPointEditLocation.objects.get(
        parking_point=parking_point
    )

    vote = ParkingPointEditLocationVote.objects.get(
        parking_point_edit_location=proposal,
        user=user,
    )

    assert vote.is_like is None



@pytest.mark.django_db
def test_post_edit_location_requires_auth(api_client, parking_point):
    response = api_client.post(
        f"/api/parking-points/{parking_point.id}/edit-location/",
        {"location": {"lat": 50, "lng": 20}},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------
# ParkingPointEditLocationVoteView
# ---------------------------------------------------------
@pytest.mark.django_db
def test_post_vote_creates_vote(user_factory, api_client, proposal):
    user = user_factory()
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/parking-points/{proposal.parking_point.id}/edit-location/vote/",
        {"is_like": True},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    vote = ParkingPointEditLocationVote.objects.get(
        parking_point_edit_location=proposal,
        user=user,
    )
    assert vote.is_like is True


@pytest.mark.django_db
def test_post_vote_fails_without_proposal(
    api_client, user_factory, parking_point
):
    user = user_factory()
    api_client.force_authenticate(user=user)

    response = api_client.post(
        f"/api/parking-points/{parking_point.id}/edit-location/vote/",
        {"is_like": True},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_put_vote_updates_existing_vote(
    api_client, user_factory, proposal
):
    user = user_factory()
    api_client.force_authenticate(user=user)

    vote = ParkingPointEditLocationVote.objects.create(
        parking_point_edit_location=proposal,
        user=user,
        is_like=True,
    )

    response = api_client.put(
        f"/api/parking-points/{proposal.parking_point.id}/edit-location/vote/",
        {"is_like": False},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    vote.refresh_from_db()
    assert vote.is_like is False


@pytest.mark.django_db
def test_put_vote_requires_existing_vote(
    api_client, user_factory, proposal
):
    user = user_factory()
    api_client.force_authenticate(user=user)

    response = api_client.put(
        f"/api/parking-points/{proposal.parking_point.id}/edit-location/vote/",
        {"is_like": True},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
