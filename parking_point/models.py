from django.db import models
from django.contrib.gis.db import models as gis_models # Import dla pól GIS
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
    # Pole dla szerokości i długości geograficznej (PostGIS)
    original_location = gis_models.PointField(
        verbose_name="original-coordinates", srid=4326, null=False, blank=False
    )
    location = gis_models.PointField(
        verbose_name="current-location", srid=4326, null=False, blank=False
    )
    # Metadane czasowe
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Ostatnia aktualizacja"
    )
    address = models.CharField(
        max_length=255, verbose_name="Address", null=True, blank=True
    )
    marked_for_deletion_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.address)

    def recompute_location(self):
        from parking_point.utils.location_clustering import (
            update_parking_point_location,
        )

        update_parking_point_location(self)

    def save(self, *args, **kwargs):
        # Logika inicjalizacji (pamiętaj, że original_location musi być w modelu)
        if not self.pk:
            if self.location and not getattr(self, "original_location", None):
                self.original_location = self.location

        super().save(*args, **kwargs)
