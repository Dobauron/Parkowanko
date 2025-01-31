import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestRegisterView:
    client = APIClient()

    def test_register_user_successful(self):
        data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "securepassword",
        }

        response = self.client.post(
            "/api/auth/register/", data, format="json"
        )  # Dodaj pełną ścieżkę URL
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "Account created successfully"
        assert response.data["user"]["email"] == data["email"]
        assert response.data["user"]["username"] == data["username"]

        # Sprawdzenie, czy użytkownik został zapisany w bazie danych
        user = get_user_model().objects.get(email=data["email"])
        assert user.check_password(data["password"])

    @pytest.mark.django_db
    class TestRegisterView:
        client = APIClient()

        def test_register_user_invalid_data(self):
            data = {
                "email": "invalidemail",  # Niepoprawny adres email
                "username": "",  # Pusty username
                "password": "short",  # Zbyt krótkie hasło
            }

            response = self.client.post(
                "/api/auth/register/", data, format="json"
            )  # Dodaj pełną ścieżkę URL
            assert response.status_code == 400  # Oczekujemy błędu 400 (bad request)

            # Sprawdź, czy odpowiedź zawiera błędy dla 'email' i 'username'
            assert "email" in response.data
            assert "username" in response.data
            assert (
                "password" not in response.data
            )  # Hasło nie jest walidowane, jeśli inne pola są błędne
            assert response.data["email"] == ["Enter a valid email address."]
            assert response.data["username"] == ["This field may not be blank."]


@pytest.mark.django_db
class TestChangePasswordView:
    client = APIClient()

    def test_change_password_successful(self):
        user = get_user_model().objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="securepassword",
        )
        self.client.force_authenticate(user=user)

        data = {
            "old_password": "securepassword",
            "new_password": "newsecurepassword",
        }

        response = self.client.post(
            "/api/auth/change-password/", data, format="json"
        )  # Dodaj pełną ścieżkę URL
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Password has been changed successfully."

        user.refresh_from_db()
        assert user.check_password("newsecurepassword")

    def test_change_password_wrong_old_password(self):
        user = get_user_model().objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="securepassword",
        )
        self.client.force_authenticate(user=user)

        data = {
            "old_password": "wrongpassword",  # Błędne stare hasło
            "new_password": "newsecurepassword",
        }

        response = self.client.post(
            "/api/auth/change-password/", data, format="json"
        )  # Dodaj pełną ścieżkę URL
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data
        assert response.data["old_password"] == ["Wrong password."]

    def test_change_password_invalid_data(self):
        user = get_user_model().objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="securepassword",
        )
        self.client.force_authenticate(user=user)

        data = {
            "old_password": "securepassword",
            "new_password": "short",  # Zbyt krótkie nowe hasło
        }

        response = self.client.post(
            "/api/auth/change-password/", data, format="json"
        )  # Dodaj pełną ścieżkę URL
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
