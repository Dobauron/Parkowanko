import pytest
from rest_framework.exceptions import ValidationError
from parking_point.api.serializers import ParkingPointSerializer
from parking_point.models import ParkingPoint
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestParkingPointSerializer:
    @pytest.fixture
    def user(self):
        """Tworzy użytkownika testowego"""
        return get_user_model().objects.create_user(
            email="test@example.com", password="testpass"
        )

    @pytest.fixture
    def valid_data(self, user):
        """Przykładowe poprawne dane dla serializera"""
        return {
            "name": "Test Parking",
            "location": {"lat": 52.2297, "lng": 21.0122},
            "user": user.id,
        }

    def test_valid_serialization(self, valid_data):
        """Test poprawnej serializacji danych"""
        serializer = ParkingPointSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_location_field(self, valid_data):
        """Test braku pola location"""
        valid_data.pop("location")
        serializer = ParkingPointSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "error" in serializer.errors

    def test_invalid_location_format(self, valid_data):
        """Test nieprawidłowego formatu współrzędnych"""
        valid_data["location"] = {"lat": "invalid", "lng": "invalid"}
        serializer = ParkingPointSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "Nieprawidłowe dane lokalizacji" in str(serializer.errors)
        assert "error" in serializer.errors

    def test_location_too_close(self, valid_data, user):
        """Test sprawdzający, czy serializer wykrywa zbyt bliskie punkty"""
        existing_point = ParkingPoint.objects.create(
            name="Existing Parking",
            location={"lat": 52.2297, "lng": 21.0122},
            user=user,
        )

        # Nowy punkt jest bardzo blisko (powinien zwrócić błąd)
        serializer = ParkingPointSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "Nowa lokalizacja znajduje się zbyt blisko" in str(serializer.errors)
        assert "error" in serializer.errors

    def test_validate_location_empty(self, valid_data):
        """Test walidacji pustego pola location"""
        valid_data["location"] = None
        serializer = ParkingPointSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "Pole location jest wymagane." in str(serializer.errors)
        assert "error" in serializer.errors
