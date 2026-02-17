from rest_framework import generics
from .serializers import (
    RegisterSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
)
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from json import loads
import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from auth_system.services.auth import build_jwt_payload
from rest_framework_simplejwt.views import TokenRefreshView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, VerifyEmailView, ResendEmailVerificationView as BaseResendView
from allauth.account.utils import send_email_confirmation
from rest_framework.throttling import ScopedRateThrottle
from django.conf import settings # Dodano import settings

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Wysyłamy e-mail weryfikacyjny
        send_email_confirmation(request, user)

        return Response(
            {"detail": "Wysłano e-mail weryfikacyjny."},
            status=status.HTTP_201_CREATED
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
                    {"old_password": ["Błędne hasło."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"detail": "Hasło zostało pomyślnie zmienione."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(
            {"detail": "Konto zostało pomyślnie usunięte."},
            status=status.HTTP_204_NO_CONTENT
        )


class ResendEmailVerificationView(BaseResendView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'resend_email'


User = get_user_model()


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # callback_url musi być identyczny z redirect_uri użytym przez frontend
    # Pobieramy go z settings.FRONTEND_URL (np. https://parkowanko.pages.dev)
    # Jeśli frontend używa konkretnej ścieżki, np. /auth/google/callback, dodaj ją tutaj
    callback_url = settings.FRONTEND_URL 
    client_class = OAuth2Client

class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client
    # callback_url zależy od konfiguracji frontendu
    callback_url = settings.FRONTEND_URL


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
