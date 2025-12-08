from django.apps import AppConfig


class ReportPoiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Reviews"

    def ready(self):
        import Reviews.signals