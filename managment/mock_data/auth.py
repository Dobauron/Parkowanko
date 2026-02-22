from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress # Import EmailAddress

User = get_user_model()


def create_users():
    users_data = [
        "alice@test.pl",
        "bob@test.pl",
        "charlie@test.pl",
        "diana@test.pl",
        "eve@test.pl",
    ]

    users = {}

    for email in users_data:
        username = email.split("@")[0]  # ustawiamy username na część przed @
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "is_active": True,
            },
        )
        if created:
            user.set_password("test1234")
            user.save(update_fields=["password", "username", "is_active"])
            
            # Automatyczna weryfikacja e-maila dla userów testowych
            EmailAddress.objects.create(
                user=user,
                email=email,
                verified=True,
                primary=True
            )
        else:
            # upewniamy się, że username jest ustawione, jeśli użytkownik już istnieje
            if not user.username:
                user.username = username
                user.save(update_fields=["username"])

        users[username] = user

    # Dodaj konto admina
    admin_email = "admin@admin.com"
    admin_username = "admin"
    admin_user, created = User.objects.get_or_create(
        email=admin_email,
        defaults={
            "username": admin_username,
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin_user.set_password("adminadmin")
        admin_user.save(update_fields=["password"])
        
        # Automatyczna weryfikacja e-maila dla admina
        EmailAddress.objects.create(
            user=admin_user,
            email=admin_email,
            verified=True,
            primary=True
        )

    users["admin"] = admin_user

    return users
