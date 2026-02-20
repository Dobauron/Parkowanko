from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from django_rest_passwordreset.views import (
    ResetPasswordRequestToken,
    ResetPasswordConfirm,
    ResetPasswordValidateToken,
)
from .views import (
    RegisterView,
    ChangePasswordView,
    FacebookLoginView,
    LoginView,
    CustomTokenRefreshView,
    DeleteAccountView,
    ResendEmailVerificationView,
    GoogleOneTapLoginView,
)

urlpatterns = [
    # Social Auth
    path("social/google/credential/", GoogleOneTapLoginView.as_view(), name="google_one_tap_login"),
    path("social/facebook/", FacebookLoginView.as_view(), name="facebook_login"),
    
    # Standard Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("user/delete/", DeleteAccountView.as_view(), name="delete_account"),
    
    # Password Reset
    path(
        "password-reset/",
        ResetPasswordRequestToken.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/confirm/",
        ResetPasswordConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/validate-token/",
        ResetPasswordValidateToken.as_view(),
        name="password_reset_validate_token",
    ),
    
    # Email Verification
    path("register/confirm-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    
    path(
        "register/resend-confirm-email/",
        ResendEmailVerificationView.as_view(),
        name="account_email_verification_sent",
    ),
    
    path(
        "account-confirm-email/<str:key>/",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
]
