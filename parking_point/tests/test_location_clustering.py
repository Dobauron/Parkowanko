import pytest
from django.contrib.auth import get_user_model
from parking_point.models import ParkingPoint
from parking_point_edit_location.models import ParkingPointEditLocation
from parking_point.utils.location_clustering import update_parking_point_location

User = get_user_model()


@pytest.mark.django_db
class TestParkingPointLocationConsensus:

    @pytest.fixture
    def users(self):
        # Tworzy zestaw użytkowników testowych
        return [
            User.objects.create_user(
                email=f"user{i}@test.pl", username=f"user{i}", password="test1234"
            )
            for i in range(1, 8)
        ]

    @pytest.fixture
    def parking(self):
        # Tworzy ParkingPoint z początkową lokalizacją
        return ParkingPoint.objects.create(
            location={"lat": 52.2297, "lng": 21.0122},
            current_location={"lat": 52.2297, "lng": 21.0122},
            address="Test",
        )

    # ------------------------------------------------------------
    # Test 1: brak zgłoszeń → pinezka pozostaje w oryginale
    # ------------------------------------------------------------
    def test_no_suggestions_fallback(self, parking):
        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.current_location == parking.location

    # ------------------------------------------------------------
    # Test 2: mniej niż 3 zgłoszenia → brak zmiany lokalizacji
    # ------------------------------------------------------------
    def test_less_than_3_suggestions_fallback(self, parking, users):
        ParkingPointEditLocation.objects.create(
            user=users[0],
            parking_point=parking,
            location={"lat": 52.22971, "lng": 21.01221},
        )
        ParkingPointEditLocation.objects.create(
            user=users[1],
            parking_point=parking,
            location={"lat": 52.22972, "lng": 21.01222},
        )

        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.current_location == parking.location

    # ------------------------------------------------------------
    # Test 3: 3 bliskie zgłoszenia → pinezka ustawiona na medianie
    # ------------------------------------------------------------
    def test_three_close_suggestions_creates_new_location(self, parking, users):
        ParkingPointEditLocation.objects.create(
            user=users[0],
            parking_point=parking,
            location={"lat": 52.22971, "lng": 21.01221},
        )
        ParkingPointEditLocation.objects.create(
            user=users[1],
            parking_point=parking,
            location={"lat": 52.22972, "lng": 21.01222},
        )
        ParkingPointEditLocation.objects.create(
            user=users[2],
            parking_point=parking,
            location={"lat": 52.22973, "lng": 21.01223},
        )

        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.current_location != parking.location
        assert abs(parking.current_location["lat"] - 52.22972) < 0.00001

    # ------------------------------------------------------------
    # Test 4: dwa klastry → wygrywa klaster z większą liczbą zgłoszeń
    # ------------------------------------------------------------
    def test_two_clusters_bigger_wins(self, parking, users):
        # klaster 1 (3 osoby)
        ParkingPointEditLocation.objects.create(
            user=users[0],
            parking_point=parking,
            location={"lat": 52.22971, "lng": 21.01221},
        )
        ParkingPointEditLocation.objects.create(
            user=users[1],
            parking_point=parking,
            location={"lat": 52.22972, "lng": 21.01222},
        )
        ParkingPointEditLocation.objects.create(
            user=users[2],
            parking_point=parking,
            location={"lat": 52.22973, "lng": 21.01223},
        )

        # klaster 2 (4 osoby)
        ParkingPointEditLocation.objects.create(
            user=users[3],
            parking_point=parking,
            location={"lat": 52.23050, "lng": 21.01300},
        )
        ParkingPointEditLocation.objects.create(
            user=users[4],
            parking_point=parking,
            location={"lat": 52.23051, "lng": 21.01301},
        )
        ParkingPointEditLocation.objects.create(
            user=users[5],
            parking_point=parking,
            location={"lat": 52.23052, "lng": 21.01302},
        )
        ParkingPointEditLocation.objects.create(
            user=users[6],
            parking_point=parking,
            location={"lat": 52.23053, "lng": 21.01303},
        )

        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert abs(parking.current_location["lat"] - 52.230515) < 0.00001

    # ------------------------------------------------------------
    # Test 5: usunięcie zgłoszenia → pinezka wraca do oryginału
    # ------------------------------------------------------------
    def test_delete_recalculates_location(self, parking, users):
        e1 = ParkingPointEditLocation.objects.create(
            user=users[0],
            parking_point=parking,
            location={"lat": 52.22971, "lng": 21.01221},
        )
        e2 = ParkingPointEditLocation.objects.create(
            user=users[1],
            parking_point=parking,
            location={"lat": 52.22972, "lng": 21.01222},
        )
        e3 = ParkingPointEditLocation.objects.create(
            user=users[2],
            parking_point=parking,
            location={"lat": 52.22973, "lng": 21.01223},
        )

        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.current_location != parking.location

        e3.delete()
        update_parking_point_location(parking)
        parking.refresh_from_db()
        assert parking.current_location == parking.location
