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
    DeleteAccountView,
)

urlpatterns = [
    # Social Auth
    path("social/google/", GoogleLoginView.as_view(), name="google_login"),
    path("social/facebook/", FacebookLoginView.as_view(), name="facebook_login"),
    
    # Standard Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("user/delete/", DeleteAccountView.as_view(), name="delete_account"),
    path(
        "password-reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    
    # Email Verification
    # Endpoint dla frontendu (POST z kluczem)
    path("register/confirm-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    
    # Endpoint do ponownego wysłania maila (POST z emailem)
    path(
        "register/resend-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    
    # Endpoint wewnętrzny dla allauth (musi zostać, ale ukryjemy go w Swaggerze jeśli chcesz)
    path(
        "account-confirm-email/<str:key>/",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
]
