from django.db import models
from auth_system.models import Account
from multiselectfield import MultiSelectField

class ParkingPoint(models.Model):
    # Podstawowe metadane
    PROPERTY_CHOICES = (
        ("camera", "Monitoring"),
        ("covered", "Zadaszony"),
        ("ev", "Ładowanie EV"),
        ("paid", "Płatny"),
        ("guarded", "Strzeżony"),
        ("dangerous_district", "niebezpieczny_rejon"),
    )
    OCCUPANCY_CHOICES = (
        ("HIGH", "high"),
        ("MEDIUM", "medium"),
        ("LOW", "low"),
    )

    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parking_point",
    )
    # Pole dla szerokości i długości geograficznej
    location = models.JSONField(verbose_name="coordynaty", null=False, blank=False)
    properties = MultiSelectField(choices=PROPERTY_CHOICES, blank=True, null=True)
    occupancy = models.CharField(choices=OCCUPANCY_CHOICES, max_length=255, blank=True, null=True)
    # Metadane czasowe
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Ostatnia aktualizacja"
    )


    def __str__(self):
        return self.name

    def check_and_delete(self):
        if self.reports.count() >= 3:
            self.delete()
