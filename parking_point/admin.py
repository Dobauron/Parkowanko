from django.contrib import admin
from .models import ParkingPoint

@admin.register(ParkingPoint)
class ParkingPointAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
