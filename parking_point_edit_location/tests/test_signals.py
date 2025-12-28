import pytest
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import (
    ParkingPointEditLocation,
    ParkingPointEditLocationVote,
)

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def user_factory(db, django_user_model):
    def create_user(email=None, username=None):
        import uuid

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
# Tests
# ============================================================


@pytest.mark.django_db
def test_set_has_proposal_on_create(parking_point, user_factory):
    # przed utworzeniem propozycji flaga = False
    assert parking_point.has_edit_location_proposal is False

    user = user_factory()
    ParkingPointEditLocation.objects.create(
        user=user, parking_point=parking_point, location={"lat": 52.0001, "lng": 21.0}
    )

    # Po utworzeniu flaga powinna być True
    parking_point.refresh_from_db()
    assert parking_point.has_edit_location_proposal is True


@pytest.mark.django_db
def test_apply_vote_effect_approve(proposal, user_factory):
    # Dodajemy 3 likes, żeby zatwierdzić lokalizację
    users = [user_factory() for _ in range(3)]
    for u in users:
        ParkingPointEditLocationVote.objects.create(
            user=u, parking_point_edit_location=proposal, is_like=True
        )

    # proposal powinien być usunięty, a lokalizacja ParkingPoint zaktualizowana
    proposal.parking_point.refresh_from_db()
    assert proposal.parking_point.location == proposal.location
    assert ParkingPointEditLocation.objects.filter(pk=proposal.pk).count() == 0
    assert proposal.parking_point.has_edit_location_proposal is False


@pytest.mark.django_db
def test_apply_vote_effect_reject(proposal, user_factory):
    # Dodajemy 3 dislikes, żeby odrzucić propozycję
    users = [user_factory() for _ in range(3)]
    for u in users:
        ParkingPointEditLocationVote.objects.create(
            user=u, parking_point_edit_location=proposal, is_like=False
        )

    # proposal powinien być usunięty, lokalizacja ParkingPoint nie zmieniona
    proposal.parking_point.refresh_from_db()
    assert ParkingPointEditLocation.objects.filter(pk=proposal.pk).count() == 0
    assert proposal.parking_point.location != proposal.location
    assert proposal.parking_point.has_edit_location_proposal is False


@pytest.mark.django_db
def test_apply_vote_effect_partial_votes(proposal, user_factory):
    # 2 likes i 1 dislike → jeszcze nie zatwierdzamy
    users = [user_factory() for _ in range(2)]
    for u in users:
        ParkingPointEditLocationVote.objects.create(
            user=u, parking_point_edit_location=proposal, is_like=True
        )
    ParkingPointEditLocationVote.objects.create(
        user=user_factory(), parking_point_edit_location=proposal, is_like=False
    )

    proposal.parking_point.refresh_from_db()
    # Proposal nadal istnieje
    assert ParkingPointEditLocation.objects.filter(pk=proposal.pk).exists()
    # Flaga powinna pozostać True
    assert proposal.parking_point.has_edit_location_proposal is True
