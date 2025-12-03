from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from parking_point.models import ParkingPoint
from django.contrib.auth import get_user_model
from django.db import transaction
User = get_user_model()


class Review(models.Model):
    class Attribiutes(models.TextChoices):
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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_point = models.ForeignKey(
        ParkingPoint, on_delete=models.PROTECT, related_name="reviews"
    )
    description = models.TextField(blank=True, null=True)  # Tylko dla "Inne"
    attribiutes = ArrayField(
        models.CharField(max_length=20, choices=Attribiutes.choices),
        default=list,
        blank=True,
        help_text=_("Lista właściwości, które użytkownik zgłasza."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    occupancy = models.CharField(
        null=True, blank=True, max_length=255, choices=Occupancy.choices
    )

    class Meta:
        unique_together = (
            "user",
            "parking_point",
        )  # Jeden użytkownik może zgłosić dany punkt tylko raz

    def __str__(self):
        return f"{self.user} zgłosił {self.parking_point}"



