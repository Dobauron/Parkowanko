from django.db import models
from parking_point.models import ParkingPoint
from django.contrib.auth import get_user_model

User = get_user_model()


class ParkingPointEditLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_point = models.ForeignKey(
        ParkingPoint, on_delete=models.CASCADE, related_name="location_edits"
    )
    location = models.JSONField(verbose_name="coordynaty")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Każdy user może mieć max 1 propozycję na parking_point
        unique_together = ("user", "parking_point")

    def __str__(self):
        return f"{self.user} chce zmienić ParkingPoint id={self.parking_point.id}"
