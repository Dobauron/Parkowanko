from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from .views import (
    RegisterView,
    ChangePasswordView,
    GoogleLoginView,
    FacebookLoginView,
    LoginView,
    CustomTokenRefreshView,
)

urlpatterns = [
    path("google/", GoogleLoginView.as_view(), name="google_login"),
    path("facebook/", FacebookLoginView.as_view(), name="facebook_login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "password-reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    # Weryfikacja e-maila
    path("verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path(
        "account-confirm-email/<str:key>/",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "register/account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
]
