from rest_framework import generics
from .serializers import RegisterSerializer, ChangePasswordSerializer, GoogleLoginSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from json import loads
import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.conf import settings
from auth_system.models import Account



class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": {
                    "email": user.email,
                    "username": user.username,
                },
                "message": "Account created successfully",
            },
            status=status.HTTP_201_CREATED,
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



@extend_schema(
    summary="Logowanie przez Google",
    description="Weryfikuje Google ID Token i zwraca JWT (access + refresh).",
    request=GoogleLoginSerializer,
    responses={
        200: OpenApiExample(
            "Login poprawny",
            value={
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                "user": {
                    "id": 1,
                    "email": "test@gmail.com",
                    "first_name": "Jan",
                    "last_name": "Kowalski"
                }
            }
        ),
        400: OpenApiExample(
            "Token nieprawidłowy",
            value={"error": "Nieprawidłowy token Google"}
        )
    }
)
class GoogleLoginView(APIView):
    def post(self, request):
        """
        Logowanie użytkownika za pomocą tokena Google OAuth2 i zwracanie JWT.
        """
        # Walidacja danych wejściowych
        serializer = GoogleLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Brak tokena", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = serializer.validated_data['token']

        # Weryfikacja tokena Google z walidacją audience
        google_url = f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
        google_response = requests.get(google_url)

        if google_response.status_code != 200:
            return Response(
                {"error": "Nieprawidłowy token Google"},
                status=status.HTTP_400_BAD_REQUEST
            )

        google_data = google_response.json()
        email = google_data.get("email")

        # WALIDACJA - sprawdź czy token jest dla twojej aplikacji
        if google_data.get("aud") != settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:
            return Response(
                {"error": "Token nie jest przeznaczony dla tej aplikacji"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not email:
            return Response(
                {"error": "Brak emaila w odpowiedzi Google"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sprawdzenie, czy użytkownik istnieje lub utworzenie nowego
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            # Tworzenie nowego użytkownika z danymi z Google
            user = Account.objects.create(
                email=email,
                username=email,  # lub google_data.get("name", "").replace(" ", "_")
                first_name=google_data.get("given_name", ""),
                last_name=google_data.get("family_name", ""),
                is_active=True
            )
            user.set_unusable_password()  # Użytkownik loguje się tylko przez Google
            user.save()

        # Generowanie tokena JWT
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            },
            status=status.HTTP_200_OK
        )