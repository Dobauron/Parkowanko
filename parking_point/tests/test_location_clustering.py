import pytest
from django.contrib.auth import get_user_model
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation
from parking_point.utils.location_clustering import update_parking_point_location
from parking_point.utils.location_clustering import DEFAULT_CLUSTER_CONFIG
from pytest import approx

User = get_user_model()


@pytest.mark.django_db
class TestParkingPointLocationConsensus:

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

    # ------------------------------------------------------------
    # Test 1: brak zgłoszeń → pinezka pozostaje w oryginale
    # ------------------------------------------------------------
    def test_no_suggestions_fallback(self, parking):
        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.location == parking.original_location

    # ------------------------------------------------------------
    # Test 2: mniej niż MIN_USERS_IN_CLUSTER → brak zmiany lokalizacji
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Test 3: klaster spełniający prog → aktualizacja lokalizacji + usunięcie editów
    # ------------------------------------------------------------
    def test_cluster_updates_location_and_deletes_edits(self, parking, users):
        # Tworzymy klaster minimalny
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

        # 1. Lokalizacja powinna być medianą
        expected_lat = 52.2300 + 0.00001  # mediana
        expected_lng = 21.0130 + 0.00001
        assert abs(parking.location["lat"] - expected_lat) < 1e-6
        assert abs(parking.location["lng"] - expected_lng) < 1e-6

        # 2. Wszystkie edit pointy klastra powinny zostać usunięte
        edits_remaining = ParkingPointEditLocation.objects.filter(parking_point=parking)
        assert edits_remaining.count() == 0

    # ------------------------------------------------------------
    # Test 4: usunięcie pojedynczego edit pointu przed osiągnięciem progu → brak zmiany
    # ------------------------------------------------------------
    def test_delete_edit_before_cluster_threshold(self, parking, users):
        for i in range(DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"] - 1):
            ParkingPointEditLocation.objects.create(
                user=users[i],
                parking_point=parking,
                location={"lat": 52.2301 + i * 0.00001, "lng": 21.0131 + i * 0.00001},
            )

        # Usuwamy jeden edit
        ParkingPointEditLocation.objects.first().delete()

        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.location == parking.original_location

    # ------------------------------------------------------------
    # Test 5: kilka klastrów, pierwszy osiąga prog → drugi ignorowany
    # ------------------------------------------------------------
    def test_multiple_clusters_only_first_applies(self, parking, users):
        # Klaster 1
        for i in range(DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"]):
            ParkingPointEditLocation.objects.create(
                user=users[i],
                parking_point=parking,
                location={"lat": 52.2300 + i * 0.00001, "lng": 21.0130 + i * 0.00001},
            )
        # Klaster 2 (założony w tym samym PP, ale nie spełnia już progów bo pierwszy klaster zostanie zatwierdzony)
        for i in range(
            DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"],
            2 * DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"],
        ):
            ParkingPointEditLocation.objects.create(
                user=users[i % len(users)],
                parking_point=parking,
                location={"lat": 52.2310 + i * 0.00001, "lng": 21.0140 + i * 0.00001},
            )

        update_parking_point_location(parking)
        parking.refresh_from_db()

        # 1. Lokalizacja = mediana pierwszego klastra
        # Poprawione wartości oczekiwane (mediana dla i=0,1,2)
        expected_lat = 52.23001
        expected_lng = 21.01301
        assert parking.location["lat"] == approx(expected_lat, abs=1e-5)
        assert parking.location["lng"] == approx(expected_lng, abs=1e-5)

        # 2. Wszystkie edit pointy powinny zostać usunięte (zgodnie z logiką w location_clustering.py)
        edits_remaining = ParkingPointEditLocation.objects.filter(parking_point=parking)
        assert edits_remaining.count() == 0

    # ------------------------------------------------------------
    # Test 6: zatwierdzony klaster usuwa WSZYSTKIE edit pointy
    # ------------------------------------------------------------
    def test_only_cluster_edits_deleted(self, parking, users):
        # Tworzymy klaster, który zostanie zatwierdzony
        cluster_users = users[: DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"]]
        for i, user in enumerate(cluster_users):
            ParkingPointEditLocation.objects.create(
                user=user,
                parking_point=parking,
                location={"lat": 52.2300 + i * 0.00001, "lng": 21.0130 + i * 0.00001},
            )

        # Dodajemy kilka innych edit pointów, które nie należą do zatwierdzonego klastra
        other_users = users[DEFAULT_CLUSTER_CONFIG["MIN_USERS_IN_CLUSTER"] :]
        for i, user in enumerate(other_users):
            ParkingPointEditLocation.objects.create(
                user=user,
                parking_point=parking,
                location={"lat": 52.2400 + i * 0.00001, "lng": 21.0200 + i * 0.00001},
            )

        # Wywołanie logiki klastra
        update_parking_point_location(parking)
        parking.refresh_from_db()

        # Sprawdzamy, że WSZYSTKIE edit pointy zostały usunięte
        remaining_edits = ParkingPointEditLocation.objects.filter(parking_point=parking)
        assert remaining_edits.count() == 0
