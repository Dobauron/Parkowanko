from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    RegisterView,
    ChangePasswordView,
    GoogleLoginView,
    LoginView,
    CustomTokenRefreshView,
)

urlpatterns = [
    # path("google/", GoogleLoginView.as_view(), name="google_login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
