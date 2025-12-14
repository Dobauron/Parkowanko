from rest_framework import generics
from .serializers import RegisterSerializer, ChangePasswordSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from json import loads
import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_system.services.auth import build_auth_response
from rest_framework_simplejwt.views import TokenObtainPairView

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            build_auth_response(user),
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,  # Definiuje schemat dla danych wejściowych (żądania)
        responses={200: None},  # Definiuje schemat dla odpowiedzi
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            if not user.check_password(old_password):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"detail": "Password has been changed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()


class GoogleLoginView(APIView):
    def post(self, request):
        """
        Logowanie użytkownika za pomocą tokena Google OAuth2 i zwracanie JWT.
        """
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Brak tokena"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Weryfikacja tokena Google
        google_url = f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
        google_response = requests.get(google_url)

        if google_response.status_code != 200:
            return Response(
                {"error": "Nieprawidłowy token"}, status=status.HTTP_400_BAD_REQUEST
            )

        google_data = loads(google_response.text)
        email = google_data.get("email")

        if not email:
            return Response(
                {"error": "Brak emaila w odpowiedzi Google"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sprawdzenie, czy użytkownik istnieje
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email}
        )

        # Generowanie tokena JWT
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
