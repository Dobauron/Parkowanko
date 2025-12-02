from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "parking_point",
        "show_properties",
        "occupancy",
        "is_liked",
        "created_at",
    )
    list_filter = ("occupancy", "is_liked", "created_at")
    search_fields = (
        "user__username",
        "parking_point__name",
        "description",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Informacje o zgłoszeniu",
            {
                "fields": (
                    "user",
                    "parking_point",
                    "properties",
                    "occupancy",
                    "is_liked",
                    "description",
                    "created_at",
                )
            },
        ),
    )

    def show_properties(self, obj):
        """Ładne wyświetlanie ArrayField z właściwościami."""
        if not obj.properties:
            return "—"
        return ", ".join(obj.properties)

