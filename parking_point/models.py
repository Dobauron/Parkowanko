from django.db import models
from auth_system.models import Account
from multiselectfield import MultiSelectField
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class ParkingPoint(models.Model):
    user = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parking_point",
    )
    # Pole dla szerokości i długości geograficznej
    original_location = models.JSONField(
        verbose_name="original-coordinates", null=False, blank=False
    )
    location = models.JSONField(verbose_name="current-location", null=True, blank=True)
    # Metadane czasowe
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Ostatnia aktualizacja"
    )
    address = models.CharField(
        max_length=255, verbose_name="Address", null=True, blank=True
    )

    def __str__(self):
        return str(self.address)

    def recompute_location(self):
        from parking_point.utils.location_clustering import (
            update_parking_point_location,
        )

        update_parking_point_location(self)

    def save(self, *args, **kwargs):
        if not self.pk and self.location is None:
            self.location = self.original_location
        super().save(*args, **kwargs)
