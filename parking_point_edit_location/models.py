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
    updated_at = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user} want edit ParkingPoint id = {self.parking_point}"
