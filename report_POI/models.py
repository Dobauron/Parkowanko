from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from parking_point.models import ParkingPoint

User = get_user_model()


class ParkingPointReport(models.Model):
    class ReportReason(models.TextChoices):
        PAID = "paid", _("Miejsce jest płatne")
        NOT_PARKING = "not_parking", _("Miejsce nie jest parkingiem")
        OTHER = "other", _("Inne")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_point = models.ForeignKey(
        ParkingPoint, on_delete=models.CASCADE, related_name="reports"
    )
    reason = models.CharField(max_length=20, choices=ReportReason.choices)
    description = models.TextField(blank=True, null=True)  # Tylko dla "Inne"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "parking_point",
        )  # Jeden użytkownik może zgłosić dany punkt tylko raz

    def __str__(self):
        return f"{self.user} zgłosił {self.parking_point} ({self.reason})"
