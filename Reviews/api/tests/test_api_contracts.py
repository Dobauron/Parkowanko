import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils.timezone import now
from parking_point.models import ParkingPoint
from Reviews.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestReviewAPIContract:
    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="password123"
        )

        self.parking_owner = User.objects.create_user(
            username="owner", email="owner@owner.com", password="password123"
        )

        self.parking_point = ParkingPoint.objects.create(
            user=self.parking_owner,
            location={"lat": 52.22977, "lng": 21.01178},
        )

        self.url = reverse(
            "review",
            kwargs={"pk": self.parking_point.pk},
        )

    def normalize_response(self, data: dict) -> dict:
        """
        Normalizuje pola dynamiczne, aby dało się
        porównać kontrakt GET vs POST.
        """
        data = data.copy()
        data.pop("id", None)
        data.pop("created_at", None)
        return data

    def test_get_and_post_have_identical_contract(self):
        self.client.force_authenticate(user=self.user)

        post_payload = {
            "attributes": ["POOR_LIGHTING"],
            "occupancy": "LOW",
            "description": "Bardzo dobre miejsce",
            "is_like": False,
        }

        # --- POST ---
        post_response = self.client.post(
            self.url,
            post_payload,
            format="json",
        )
        print(post_response.status_code)
        print(post_response.json())
        assert post_response.status_code == 201
        post_data = post_response.json()

        # --- GET ---
        get_response = self.client.get(self.url)
        assert get_response.status_code == 200

        get_data = get_response.json()
        assert isinstance(get_data, list)
        assert len(get_data) == 1

        get_item = get_data[0]

        # --- CONTRACT CHECK ---
        assert set(post_data.keys()) == set(get_item.keys())

        # --- CONTENT CHECK (bez pól dynamicznych) ---
        assert self.normalize_response(post_data) == self.normalize_response(get_item)
