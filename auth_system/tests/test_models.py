import pytest
from auth_system.models import Account


@pytest.mark.django_db
def test_create_user():
    user = Account.objects.create_user(
        email="test@example.com", password="securepassword"
    )
    assert user.email == "test@example.com"
    assert user.check_password("securepassword")
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_superuser():
    superuser = Account.objects.create_superuser(
        email="admin@example.com", password="adminpassword"
    )
    assert superuser.email == "admin@example.com"
    assert superuser.check_password("adminpassword")
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.is_superuser is True


@pytest.mark.django_db
def test_create_user_without_email():
    with pytest.raises(ValueError, match="Email is required"):
        Account.objects.create_user(email="", password="password")


@pytest.mark.django_db
def test_create_superuser_without_staff():
    with pytest.raises(
        ValueError, match="Superuser must be assigned to is_staff=True."
    ):
        Account.objects.create_superuser(
            email="admin@example.com", password="password", is_staff=False
        )


@pytest.mark.django_db
def test_create_superuser_without_superuser():
    with pytest.raises(
        ValueError, match="Superuser must be assigned to is_superuser=True."
    ):
        Account.objects.create_superuser(
            email="admin@example.com", password="password", is_superuser=False
        )
