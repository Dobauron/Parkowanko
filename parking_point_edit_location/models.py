from django.db import models
from parking_point.models import ParkingPoint
from django.contrib.auth import get_user_model
User = get_user_model()


class ParkingPointEditLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_point = models.ForeignKey(
        ParkingPoint, on_delete=models.CASCADE, related_name="location_edit"
    )
    location = models.JSONField(verbose_name="coordynaty", null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user} want edit {self.parking_point}"

    # def save(self, *args, **kwargs):
    #     if ParkingPointEditLocation.objects.filter(user=self.user, parking_point=self.parking_point).exists():
    #         raise ValueError("Użytkownik może zgłosić tylko jedną zmianę lokalizacji dla tego parking point.")
    #     super().save(*args, **kwargs)
    #     # Automatycznie ustawiamy flagę w ParkingPoint
    #     pp = self.parking_point
    #     pp.has_location_edit_pending = True
    #     pp.save(update_fields=["has_location_edit_pending"])

class ParkingPointEditLocationVote(models.Model):
    parking_point_edit_location = models.ForeignKey(
        ParkingPointEditLocation,
        on_delete=models.CASCADE,
        related_name="votes"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("parking_point_edit_location", "user")  # jeden użytkownik jeden głos