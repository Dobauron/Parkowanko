import pytest
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation
from parking_point_edit_location.signals import recompute_on_save, recompute_on_delete
from parking_point.utils.location_clustering import update_parking_point_location
from parking_point.utils.location_clustering import DEFAULT_CLUSTER_CONFIG
from pytest import approx

User = get_user_model()


@pytest.mark.django_db
class TestParkingPointLocationConsensus:

    def setup_method(self):
        """Odłączamy sygnały przed każdym testem."""
        post_save.disconnect(recompute_on_save, sender=ParkingPointEditLocation)
        post_delete.disconnect(recompute_on_delete, sender=ParkingPointEditLocation)

    def teardown_method(self):
        """Podłączamy sygnały z powrotem po każdym teście."""
        post_save.connect(recompute_on_save, sender=ParkingPointEditLocation)
        post_delete.connect(recompute_on_delete, sender=ParkingPointEditLocation)

    @pytest.fixture
    def users(self):
        """Tworzy zestaw 7 testowych użytkowników"""
        return [
            User.objects.create_user(
                email=f"user{i}@test.pl", username=f"user{i}", password="test1234"
            )
            for i in range(1, 8)
        ]

    @pytest.fixture
    def parking(self):
        """Tworzy ParkingPoint z początkową lokalizacją"""
        return ParkingPoint.objects.create(
            original_location={"lat": 52.2297, "lng": 21.0122},
            location={"lat": 52.2297, "lng": 21.0122},
            address="Test Parking",
        )

    def test_no_suggestions_fallback(self, parking):
        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.location == parking.original_location

    def test_less_than_min_users_no_update(self, parking, users):
        for i in range(DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"] - 1):
            ParkingPointEditLocation.objects.create(
                user=users[i],
                parking_point=parking,
                location={
                    "lat": 52.2297 + i * 0.00001,
                    "lng": 21.0122 + i * 0.00001,
                },
            )

        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.location == parking.original_location

    def test_cluster_updates_location_and_deletes_edits(self, parking, users):
        cluster_users = users[: DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"]]
        for i, user in enumerate(cluster_users):
            ParkingPointEditLocation.objects.create(
                user=user,
                parking_point=parking,
                location={
                    "lat": 52.2300 + i * 0.00001,
                    "lng": 21.0130 + i * 0.00001,
                },
            )

        update_parking_point_location(parking)
        parking.refresh_from_db()

        expected_lat = 52.2300 + 0.00001
        expected_lng = 21.0130 + 0.00001
        assert abs(parking.location["lat"] - expected_lat) < 1e-6
        assert abs(parking.location["lng"] - expected_lng) < 1e-6

        edits_remaining = ParkingPointEditLocation.objects.filter(parking_point=parking)
        assert edits_remaining.count() == 0

    def test_delete_edit_before_cluster_threshold(self, parking, users):
        for i in range(DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"] - 1):
            ParkingPointEditLocation.objects.create(
                user=users[i],
                parking_point=parking,
                location={"lat": 52.2301 + i * 0.00001, "lng": 21.0131 + i * 0.00001},
            )

        ParkingPointEditLocation.objects.first().delete()

        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.location == parking.original_location

    def test_multiple_clusters_only_first_applies(self, parking, users):
        # Klaster 1 (większy, aby zapewnić determinizm)
        for i in range(DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"] + 1):
            ParkingPointEditLocation.objects.create(
                user=users[i],
                parking_point=parking,
                location={"lat": 52.2300 + i * 0.00001, "lng": 21.0130 + i * 0.00001},
            )
        # Klaster 2 (mniejszy)
        for i in range(
            DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"] + 1,
            len(users)
        ):
            ParkingPointEditLocation.objects.create(
                user=users[i],
                parking_point=parking,
                location={"lat": 52.2310 + i * 0.00001, "lng": 21.0140 + i * 0.00001},
            )

        update_parking_point_location(parking)
        parking.refresh_from_db()

        # Lokalizacja powinna być medianą pierwszego, większego klastra
        expected_lat = 52.230015
        expected_lng = 21.013015
        assert parking.location["lat"] == approx(expected_lat, abs=1e-5)
        assert parking.location["lng"] == approx(expected_lng, abs=1e-5)

        # Wszystkie edycje powinny zostać usunięte
        assert ParkingPointEditLocation.objects.filter(parking_point=parking).count() == 0

    def test_all_edits_deleted_after_cluster_approval(self, parking, users):
        # Tworzymy klaster, który zostanie zatwierdzony
        cluster_users = users[: DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"]]
        for i, user in enumerate(cluster_users):
            ParkingPointEditLocation.objects.create(
                user=user,
                parking_point=parking,
                location={"lat": 52.2300 + i * 0.00001, "lng": 21.0130 + i * 0.00001},
            )

        # Dodajemy inne edycje, które nie należą do klastra
        other_users = users[DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"] :]
        for i, user in enumerate(other_users):
            ParkingPointEditLocation.objects.create(
                user=user,
                parking_point=parking,
                location={"lat": 52.2400 + i * 0.00001, "lng": 21.0200 + i * 0.00001},
            )

        update_parking_point_location(parking)
        parking.refresh_from_db()

        # Sprawdzamy, że WSZYSTKIE edycje zostały usunięte, zgodnie z logiką w kodzie
        assert ParkingPointEditLocation.objects.filter(parking_point=parking).count() == 0
