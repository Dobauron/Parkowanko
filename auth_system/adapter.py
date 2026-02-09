from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

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
