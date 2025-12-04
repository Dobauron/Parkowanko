from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ParkingPointEditLocation, ParkingPointEditLocationVote


@receiver(post_save, sender=ParkingPointEditLocation)
def set_has_proposal_on_create(sender, instance, created, **kwargs):
    """
    Ustawia has_proposal = True gdy powstaje nowa propozycja
    """
    if created:
        parking_point = instance.parking_point
        if not parking_point.has_proposal:
            parking_point.has_proposal = True
            parking_point.save(update_fields=["has_proposal"])


@receiver(post_save, sender=ParkingPointEditLocationVote)
def check_score(sender, instance, created, **kwargs):
    if not created:
        return

    proposal = instance.parking_point_edit_location

    # Bilans like - dislike
    score = proposal.score

    if score >= 3:
        # Zaakceptuj
        proposal.parking_point.location = proposal.location
        proposal.parking_point.save()
        proposal.delete()

    elif score <= -3:
        # Odrzuć
        proposal.delete()
