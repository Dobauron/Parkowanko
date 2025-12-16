from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

def build_user_payload(user):
    """
    Tworzy spójny payload użytkownika do zwracania w response auth.
    """
    return {
        "id": user.id,
        "username": user.username,
        "roles": list(user.groups.values_list("name", flat=True))
    }


def build_jwt_payload(user):
    """
    Tworzy pełny response JWT wraz z access, refresh i expires_in.
    Używany w rejestracji, logowaniu z OAuth itp.
    """
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "expires_in": int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        "user": build_user_payload(user),
    }
