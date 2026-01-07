from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ParkingPointEditLocation


@receiver([post_save, post_delete], sender=ParkingPointEditLocation)
def recalc_parking_point_location(sender, instance, **kwargs):
    instance.parking_point.recompute_location()