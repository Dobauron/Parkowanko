from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from parking_point.models import ParkingPoint
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Review(models.Model):
    class Attributes(models.TextChoices):
        FREE_OFF_SEASON = "FREE_OFF_SEASON", _("Darmowy poza sezonem")
        DANGEROUS_AREA = "DANGEROUS_AREA", _("Niebezpieczna okolica")
        POOR_SURFACE = "POOR_SURFACE", _("Zła nawierzchnia")
        HARD_ACCESS = "HARD_ACCESS", _("Trudny dostęp")
        FLOOD_PRONE = "FLOOD_PRONE", _("Podatny na podtopienia")
        POOR_LIGHTING = "POOR_LIGHTING", _("Słabe oświetlenie")
        PARKING_RESTRICTIONS = "PARKING_RESTRICTIONS", _("Ograniczenia parkingowe")

    class Occupancy(models.TextChoices):
        HIGH = "HIGH", _("Wysokie")
        MEDIUM = "MEDIUM", _("Średnie")
        LOW = "LOW", _("Niskie")
        NO_SPACE = "NO_SPACE", _("Brak miejsca")
        NO_DATA = "NO_DATA", _("Brak danych")

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # nie można usunać PP kiedy istnieje recenzja
    parking_point = models.ForeignKey(
        ParkingPoint, on_delete=models.PROTECT, related_name="reviews"
    )
    description = models.TextField(blank=True, null=True)  # Tylko dla "Inne"
    attributes = ArrayField(
        models.CharField(max_length=20, choices=Attributes.choices),
        null=True,
        default=list,
        blank=True,
        help_text=_("Lista właściwości, które użytkownik zgłasza."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    occupancy = models.CharField(
        max_length=255,
        choices=Occupancy.choices,
        default=Occupancy.NO_DATA,  # lub inna wartość domyślna
        blank=False,  # nie pozwala na puste pola w formularzu
        null=False,  # nie pozwala na NULL w bazie
    )
    is_like = models.BooleanField()

    class Meta:
        unique_together = (
            "user",
            "parking_point",
        )  # Jeden użytkownik może zgłosić dany punkt tylko raz

    def __str__(self):
        return f"{self.user} zgłosił {self.parking_point}"
