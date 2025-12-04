from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ParkingPointEditLocation, ParkingPoint


@receiver(post_save, sender=ParkingPointEditLocation)
def set_has_proposal_on_create(sender, instance, created, **kwargs):
    """
    Ustawia has_proposal = True gdy powstaje nowa propozycja
    """
    if created:
        parking_point = instance.parking_point
        if not parking_point.has_proposal:
            parking_point.has_proposal = True
            parking_point.save(update_fields=['has_proposal'])