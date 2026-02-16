from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Wywołaj standardowy handler DRF, aby uzyskać podstawową odpowiedź
    response = exception_handler(exc, context)

    if response is not None:
        # Sprawdź, czy w odpowiedzi jest klucz 'detail' (standardowy dla DRF)
        if "detail" in response.data:
            msg = str(response.data["detail"])
            
            # Tłumaczenie konkretnych komunikatów
            if "The OTP password entered is not valid" in msg:
                response.data["detail"] = "Podany kod jest nieprawidłowy. Sprawdź go i spróbuj ponownie."
            
            elif "Invalid token" in msg:
                response.data["detail"] = "Nieprawidłowy token."
                
            elif "Token is invalid or expired" in msg:
                response.data["detail"] = "Token jest nieprawidłowy lub wygasł."
            
            elif "User not found" in msg:
                response.data["detail"] = "Nie znaleziono użytkownika."

            elif "Authentication credentials were not provided" in msg:
                response.data["detail"] = "Dane uwierzytelniające nie zostały podane."

    return response
