from django.contrib import admin
from .models import ParkingPointReport


@admin.register(ParkingPointReport)
class ParkingPointReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "parking_point",
        "reason",
        "created_at",
    )  # Widok listy
    list_filter = ("reason", "created_at")  # Filtry w panelu
    search_fields = (
        "user__username",
        "parking_point__name",
        "description",
    )  # Pole wyszukiwania
    ordering = ("-created_at",)  # Sortowanie (najnowsze na górze)
    readonly_fields = ("created_at",)  # Pole tylko do odczytu

    fieldsets = (
        (
            "Informacje o zgłoszeniu",
            {
                "fields": (
                    "user",
                    "parking_point",
                    "reason",
                    "description",
                    "created_at",
                ),
            },
        ),
    )
