from django.dispatch import receiver
from django.core.mail import send_mail
from django_rest_passwordreset.signals import reset_password_token_created

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Tutaj budujemy treść maila, który pójdzie do użytkownika
    print("DEBUG: Sygnał resetu hasła wystartował!")
    # URL Twojego frontendu (na razie lokalny, potem zmienisz na adres na Renderze/Vercelu)
    frontend_url = "https://zygarios.github.io/parkowanko/reset-password"

    # Tworzymy pełny link z tokenem jako parametrem
    reset_link = f"{frontend_url}?token={reset_password_token.key}"

    email_plaintext_message = (
        f"Cześć!\n\n"
        f"Kliknij w poniższy link, aby ustawić nowe hasło:\n"
        f"{reset_link}\n\n"
        f"Jeśli to nie Ty prosiłeś o reset, zignoruj tę wiadomość."
    )

    send_mail(
        "Reset hasła w aplikacji Parkowanko",
        email_plaintext_message,
        None,
        [reset_password_token.user.email],
        fail_silently=False,
    )