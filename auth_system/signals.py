from django.dispatch import receiver
from django.core.mail import send_mail
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    print("DEBUG: Sygnał resetu hasła wystartował!")
    
    # URL Twojego frontendu pobierany z settings
    frontend_url = f"{settings.FRONTEND_URL}/auth/reset-password"
    reset_link = f"{frontend_url}?token={reset_password_token.key}"

    email_plaintext_message = f"""Cześć!

Kliknij w poniższy link, aby ustawić nowe hasło:
{reset_link}

Jeśli to nie Ty prosiłeś o reset, zignoruj tę wiadomość."""

    send_mail(
        subject="Reset hasła w aplikacji Parkowanko",
        message=email_plaintext_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reset_password_token.user.email],
        fail_silently=False,
    )
