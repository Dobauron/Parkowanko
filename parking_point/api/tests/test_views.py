import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from parking_point.models import ParkingPoint


@pytest.fixture
def user():
    """Tworzymy użytkownika testowego z niestandardowym modelem użytkownika"""
    User = (
        get_user_model()
    )  # Używamy get_user_model do uzyskania niestandardowego modelu użytkownika
    return User.objects.create_user(email="testuser@gmail.com", password="password")


@pytest.fixture
def parking_point(user):
    """Tworzymy przykładowy ParkingPoint dla testów"""
    return ParkingPoint.objects.create(
        location={"lat": 52.2297, "lng": 21.0122}, user=user
    )


@pytest.fixture
def api_client():
    """APIClient do wykonywania zapytań HTTP"""
    return APIClient()


@pytest.mark.django_db  # Dodajemy oznaczenie, aby umożliwić dostęp do bazy danych w testach
# Testowanie GET - pobieranie listy ParkingPoint
def test_get_parking_points(api_client, parking_point):
    """Test sprawdzający pobranie listy obiektów ParkingPoint"""
    response = api_client.get("/api/parking-points/")
    assert response.status_code == status.HTTP_200_OK
    assert (
            len(response.data) > 0
    )  # Sprawdzamy, czy w odpowiedzi jest przynajmniej jeden obiekt


@pytest.mark.django_db  # Dodajemy oznaczenie, aby umożliwić dostęp do bazy danych w testach
# Testowanie POST - tworzenie ParkingPoint
def test_create_parking_point(api_client, user):
    """Test sprawdzający utworzenie obiektu ParkingPoint"""
    api_client.force_authenticate(user=user)  # Zaloguj użytkownika
    data = {"location": {"lat": 52.2297, "lng": 21.0122}}
    response = api_client.post("/api/parking-points/", data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "location" in response.data
    assert (
            "id" in response.data
    )  # Sprawdzamy, czy w odpowiedzi jest identyfikator nowo utworzonego obiektu

