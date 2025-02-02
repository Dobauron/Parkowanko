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
        name="Test Point", location={"lat": 52.2297, "lng": 21.0122}, user=user
    )


@pytest.fixture
def api_client():
    """APIClient do wykonywania zapytań HTTP"""
    return APIClient()


@pytest.mark.django_db  # Dodajemy oznaczenie, aby umożliwić dostęp do bazy danych w testach
# Testowanie GET - pobieranie listy ParkingPoint
def test_get_parking_points(api_client, parking_point):
    """Test sprawdzający pobranie listy obiektów ParkingPoint"""
    response = api_client.get("/api/parkings/")
    assert response.status_code == status.HTTP_200_OK
    assert (
        len(response.data) > 0
    )  # Sprawdzamy, czy w odpowiedzi jest przynajmniej jeden obiekt
    assert response.data[0]["name"] == parking_point.name


@pytest.mark.django_db  # Dodajemy oznaczenie, aby umożliwić dostęp do bazy danych w testach
# Testowanie POST - tworzenie ParkingPoint
def test_create_parking_point(api_client, user):
    """Test sprawdzający utworzenie obiektu ParkingPoint"""
    api_client.force_authenticate(user=user)  # Zaloguj użytkownika
    data = {"name": "New Parking Point", "location": {"lat": 52.2297, "lng": 21.0122}}
    response = api_client.post("/api/parkings/", data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "New Parking Point"
    assert "location" in response.data
    assert (
        "id" in response.data
    )  # Sprawdzamy, czy w odpowiedzi jest identyfikator nowo utworzonego obiektu


@pytest.mark.django_db  # Dodajemy oznaczenie, aby umożliwić dostęp do bazy danych w testach
# Testowanie PUT - aktualizacja ParkingPoint
def test_update_parking_point(api_client, parking_point, user):
    """Test sprawdzający aktualizację obiektu ParkingPoint"""
    api_client.force_authenticate(user=user)  # Zaloguj użytkownika
    updated_data = {
        "name": "Updated Parking Point",
        "location": {"lat": 52.2297, "lng": 21.0},
    }
    response = api_client.patch(
        f"/api/parkings/{parking_point.id}/", updated_data, format="json"
    )

    assert (
        response.status_code == status.HTTP_200_OK
    )  # Bad request - 400, gdy dystanse miedzy POI sie nie zgadzają
    assert response.data["name"] == "Updated Parking Point"
    assert response.data["location"] == updated_data["location"]
    assert (
        response.data["id"] == parking_point.id
    )  # Sprawdzamy, czy ID pozostało niezmienione


@pytest.mark.django_db  # Dodajemy oznaczenie, aby umożliwić dostęp do bazy danych w testach
# Testowanie PUT - nieprawidłowe dane lokalizacji
def test_update_parking_point_invalid_location(api_client, parking_point, user):
    """Test sprawdzający nieprawidłowe dane lokalizacji podczas aktualizacji"""
    api_client.force_authenticate(user=user)
    invalid_data = {
        "name": "Updated Parking Point",
        "location": {"lat": "invalid", "lng": "invalid"},
    }
    response = api_client.put(
        f"/api/parkings/{parking_point.id}/", invalid_data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Nieprawidłowe dane lokalizacji" in str(response.data)


@pytest.mark.django_db  # Dodajemy oznaczenie, aby umożliwić dostęp do bazy danych w testach
# Testowanie walidacji lokalizacji (max_distance)
def test_update_parking_point_invalid_location_distance(
    api_client, parking_point, user
):
    """Test sprawdzający walidację lokalizacji, gdzie odległość przekracza dozwoloną wartość"""
    api_client.force_authenticate(user=user)
    invalid_location_data = {
        "name": "Updated Parking Point",
        "location": {
            "lat": 52.5000,
            "lng": 21.1000,
        },  # Przykład z odległością większą niż 1000m
    }
    response = api_client.put(
        f"/api/parkings/{parking_point.id}/", invalid_location_data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Nowa lokalizacja jest zbyt oddalona od obecnej pozycji: 30641.51m (maksymalnie 1000m)."
        in str(response.data)
    )
