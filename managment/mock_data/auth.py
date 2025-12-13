from django.contrib.auth import get_user_model

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
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "is_active": True,
            },
        )
        user.set_password("test1234")
        user.save(update_fields=["password"])

        users[email.split("@")[0]] = user

    # Dodaj konto admina
    admin_email = "admin@admin.com"
    admin_user, created = User.objects.get_or_create(
        email=admin_email,
        defaults={
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin_user.set_password("adminadmin")
        admin_user.save(update_fields=["password"])
    users["admin"] = admin_user

    return users
