from django.apps import AppConfig


class ParkingPointConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "parking_point"

    def ready(self):
        # To jest kluczowe! Bez tego sygnały w ogóle nie zadziałają.
        import parking_point.signals
