from django.db.models.signals import post_save
from django.dispatch import receiver
from parking_point.models import ParkingPoint
from parking_point.utils.edit_cleanup import cleanup_foreign_edit_points


@receiver(post_save, sender=ParkingPoint)
def cleanup_on_create(sender, instance, created, **kwargs):
    if created:
        cleanup_foreign_edit_points(instance)
