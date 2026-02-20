from rest_framework import generics
from .serializers import (
    RegisterSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    GoogleOneTapSerializer,
    JWTResponseSerializer,
    ErrorResponseSerializer,
)
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from auth_system.services.auth import build_jwt_payload
from rest_framework_simplejwt.views import TokenRefreshView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, VerifyEmailView, ResendEmailVerificationView as BaseResendView
from allauth.account.utils import send_email_confirmation
from rest_framework.throttling import ScopedRateThrottle
from django.conf import settings

# Imports for Google One Tap
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth.models import Group

User = get_user_model()

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
        request=ChangePasswordSerializer,
        responses={200: None},
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


class GoogleOneTapLoginView(APIView):
    @extend_schema(
        description="Handles Google One Tap sign-in by verifying the credential token.",
        request=GoogleOneTapSerializer,
        responses={
            200: JWTResponseSerializer,
            400: ErrorResponseSerializer
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleOneTapSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credential = serializer.validated_data.get("credential")

        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                credential, google_requests.Request(), settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
            )

            email = idinfo.get("email")
            if not email:
                return Response(
                    {"error": "Email not found in token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get or create user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create a new user
                username = idinfo.get("given_name", email.split('@')[0])
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=None,  # User will log in via Google
                )
                user.is_active = True
                user.save()
                
                # Add user to the default group
                group, _ = Group.objects.get_or_create(name="USER")
                user.groups.add(group)


            # Generate JWT tokens
            jwt_payload = build_jwt_payload(user)
            return Response(jwt_payload, status=status.HTTP_200_OK)

        except ValueError as e:
            # Invalid token
            return Response(
                {"error": "Invalid token", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:4200" # Tymczasowo, do testów

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
