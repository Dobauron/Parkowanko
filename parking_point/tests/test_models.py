import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from parking_point.models import ParkingPoint


@pytest.mark.django_db
class TestParkingPointModel:

    @pytest.fixture
    def user(self):
        """Tworzymy użytkownika w bazie danych do testów"""
        User = get_user_model()  # Używamy get_user_model() zamiast Account
        return User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    @pytest.fixture
    def parking_point(self, user):
        """Tworzymy obiekt ParkingPoint powiązany z użytkownikiem"""
        return ParkingPoint.objects.create(
            user=user,
            location={
                "latitude": 52.2297,
                "longitude": 21.0122,
            },  # Przykładowe współrzędne
        )

    def test_parking_point_creation(self, parking_point):
        """Test sprawdzający poprawne utworzenie obiektu ParkingPoint"""
        assert parking_point.user.username == "testuser"
        assert parking_point.location == {"latitude": 52.2297, "longitude": 21.0122}


    def test_parking_point_created_at(self, parking_point):
        """Test sprawdzający, czy pole created_at jest automatycznie ustawiane"""
        assert parking_point.created_at is not None
        assert parking_point.created_at <= timezone.now()

    def test_parking_point_user_relation(self, parking_point, user):
        """Test sprawdzający, czy relacja z użytkownikiem działa poprawnie"""
        assert parking_point.user == user
        assert parking_point in user.parking_point.all()

    def test_parking_point_location_field(self, parking_point):
        """Test sprawdzający poprawność działania pola location"""
        assert parking_point.location == {"latitude": 52.2297, "longitude": 21.0122}
        assert isinstance(parking_point.location, dict)
        assert "latitude" in parking_point.location
        assert "longitude" in parking_point.location

    def test_parking_point_blank_fields(self, user):
        """Test sprawdzający działanie pól pustych"""
        parking_point = ParkingPoint.objects.create(
            user=None,
            location={"latitude": 52.2297, "longitude": 21.0122},
        )
        assert parking_point.user is None

    def test_parking_point_location_blank(self):
        """Test sprawdzający działanie pustego pola location"""
        with pytest.raises(ValueError):
            ParkingPoint.objects.create(
                user=self.user,
                location=None,
            )
