from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

def build_auth_response(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "expires_in": int(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        ),
        "user": {
            "id": user.id,
            "username": user.username,
            "roles": list(
                user.groups.values_list("name", flat=True)
            )
        }
    }