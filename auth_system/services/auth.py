from rest_framework_simplejwt.tokens import RefreshToken


def build_auth_response(user):
    refresh = RefreshToken.for_user(user)

    return {
        "id": user.id,
        "username": user.username,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }