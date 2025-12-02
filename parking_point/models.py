from django.db import models
from auth_system.models import Account
from multiselectfield import MultiSelectField
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

class ParkingPoint(models.Model):
    class Property(models.TextChoices):
        DIRTY = "DIRTY", _("Brudny")
        FULL = "FULL", _("Przepełniony")
        DAMAGED = "DAMAGED", _("Uszkodzony")
        UNSAFE = "UNSAFE", _("Niebezpieczny")
        OTHER = "OTHER", _("Inne")

    class Occupancy(models.TextChoices):
        FREE = "FREE", _("Wolne")
        LIMITED = "LIMITED", _("Mało miejsc")
        FULL = "FULL", _("Brak miejsc")
        UNKNOWN = "UNKNOWN", _("Nieznane")

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
    properties = ArrayField(
        models.CharField(max_length=20, choices=Property.choices),
        default=list,
        blank=True,
        help_text=_("Lista właściwości, które użytkownik zgłasza."))
    occupancy = models.CharField(
        choices=Occupancy, max_length=255, blank=True, null=True
    )
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
