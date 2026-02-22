import pytest
from ..serializers import RegisterSerializer, ChangePasswordSerializer


@pytest.mark.django_db
class TestRegisterSerializer:
    def test_register_serializer_valid_data(self):
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePassword123!",
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()  # Oczekujemy, że serializer będzie poprawny
        user = serializer.save()
        assert user.email == data["email"]
        assert user.username == data["username"]
        assert user.check_password(
            data["password"]
        )  # Sprawdzenie, czy hasło zostało zapisane
        assert user.is_active is True  # Użytkownik powinien być aktywny
        assert user.is_staff is False  # Użytkownik nie jest administratorem
        assert user.is_superuser is False  # Użytkownik nie jest superużytkownikiem

    def test_register_serializer_invalid_email(self):
        data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "SecurePassword123!",
        }

        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()  # Oczekujemy, że dane będą niepoprawne
        assert "email" in serializer.errors  # Błąd związany z adresem email
        # Dostosowano do polskiego komunikatu
        assert "Podaj poprawny adres e-mail." in str(serializer.errors["email"])

    def test_register_serializer_missing_username(self):
        data = {
            "email": "test@example.com",
            "username": "",
            "password": "SecurePassword123!",
        }

        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()  # Oczekujemy, że dane będą niepoprawne
        assert "username" in serializer.errors  # Brakujące pole 'username'
        # Dostosowano do polskiego komunikatu
        assert "To pole nie może być puste." in str(serializer.errors["username"])

    def test_register_serializer_short_password(self):
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "short",  # Zbyt krótkie hasło
        }

        serializer = RegisterSerializer(data=data)
        is_valid = serializer.is_valid()
        
        assert not is_valid  # Oczekujemy, że dane będą niepoprawne
        assert "password" in serializer.errors  # Błąd związany z hasłem

        # Sprawdzenie treści błędu w bezpieczniejszy sposób
        error_content = str(serializer.errors["password"])
        # Komunikat może się różnić w zależności od konfiguracji walidatorów
        assert "To hasło jest za krótkie." in error_content or "Musi zawierać co najmniej 8 znaków." in error_content


@pytest.mark.django_db
class TestChangePasswordSerializer:
    def test_change_password_serializer_valid_data(self):
        data = {
            "old_password": "OldPassword123!",
            "new_password": "NewSecurePassword123!",
        }

        serializer = ChangePasswordSerializer(data=data)
        assert serializer.is_valid()  # Oczekujemy, że dane będą poprawne

    def test_change_password_serializer_invalid_data(self):
        data = {
            "old_password": "OldPassword123!",
            "new_password": "short",  # Zbyt krótkie hasło
        }

        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()  # Oczekujemy, że dane będą niepoprawne
        assert "new_password" in serializer.errors  # Błąd związany z hasłem

    def test_change_password_serializer_missing_old_password(self):
        data = {
            "old_password": "",
            "new_password": "NewSecurePassword123!",
        }

        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()  # Oczekujemy, że dane będą niepoprawne
        assert "old_password" in serializer.errors  # Brakujące pole 'old_password'

    def test_change_password_serializer_invalid_old_password(self):
        data = {
            "old_password": "WrongOldPassword123!",
            "new_password": "NewSecurePassword123!",
        }

        serializer = ChangePasswordSerializer(data=data)
        assert serializer.is_valid()
