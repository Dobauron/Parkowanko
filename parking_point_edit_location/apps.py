from django.apps import AppConfig


class ParkingPointEditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "parking_point_edit_location"

    def ready(self):
        import parking_point_edit_location.signals
