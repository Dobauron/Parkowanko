from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        # URL frontendu pobierany z settings
        # Format: https://parkowanko.pages.dev/auth/potwierdz-rejestracje?token={key}
        frontend_url = f"{settings.FRONTEND_URL}/auth/potwierdz-rejestracje"
        return f"{frontend_url}?token={emailconfirmation.key}"

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Przechwytuje proces tworzenia użytkownika z danych społecznościowych.
        """
        user = super().populate_user(request, sociallogin, data)

        # Jeśli dostawca nie zwrócił nazwy użytkownika, użyj e-maila.
        # E-mail jest unikalny w systemie, więc to bezpieczne.
        if not user.username:
            user.username = user.email

        return user
