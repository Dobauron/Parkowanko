from django.db import models


class ParkingPoint(models.Model):
    # Podstawowe metadane
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # Pole dla szerokości i długości geograficznej
    location = models.JSONField(verbose_name="coordynaty", default=dict)
    # Metadane czasowe
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Ostatnia aktualizacja"
    )

    def __str__(self):
        return self.name
