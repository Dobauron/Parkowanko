import pytest
from django.db.utils import IntegrityError
from Reviews.models import Review
from parking_point.models import ParkingPoint
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_review_ok():
    user = User.objects.create_user(email="a@test.com", username="user1", password="pass")
    pp = ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0}, user=user)

    review = Review.objects.create(
        user=user,
        parking_point=pp,
        occupancy=Review.Occupancy.HIGH,
        is_like=True,
        description="Dobra lokalizacja",
        attributes=[Review.Attributes.POOR_SURFACE]
    )
    assert review.id is not None
    assert review.occupancy == Review.Occupancy.HIGH
    assert review.is_like is True
    assert Review.objects.count() == 1


@pytest.mark.django_db
def test_unique_together_user_parking_point():
    user = User.objects.create_user(email="b@test.com", username="user2", password="pass")
    pp = ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0}, user=user)

    Review.objects.create(
        user=user,
        parking_point=pp,
        occupancy=Review.Occupancy.MEDIUM,
        is_like=True
    )

    with pytest.raises(IntegrityError):
        Review.objects.create(
            user=user,
            parking_point=pp,
            occupancy=Review.Occupancy.LOW,
            is_like=False
        )


@pytest.mark.django_db
def test_attributes_default_empty_list():
    user = User.objects.create_user(email="c@test.com", username="user3", password="pass")
    pp = ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0}, user=user)

    review = Review.objects.create(
        user=user,
        parking_point=pp,
        occupancy=Review.Occupancy.NO_DATA,
        is_like=True
    )
    assert review.attributes == []


@pytest.mark.django_db
def test_str_method():
    user = User.objects.create_user(email="d@test.com", username="user4", password="pass")
    pp = ParkingPoint.objects.create(location={"lat": 52.0, "lng": 21.0}, user=user)

    review = Review.objects.create(
        user=user,
        parking_point=pp,
        occupancy=Review.Occupancy.LOW,
        is_like=False
    )
    assert str(review) == f"{user} zgłosił {pp}"
