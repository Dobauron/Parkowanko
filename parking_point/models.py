from django.db import models
from auth_system.models import Account

class ParkingPoint(models.Model):
    # Podstawowe metadane
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="parking_points")
    # Pole dla szerokości i długości geograficznej
    location = models.JSONField(verbose_name="coordynaty", null=False, blank=False)
    # Metadane czasowe
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Ostatnia aktualizacja"
    )

    def __str__(self):
        return self.name
