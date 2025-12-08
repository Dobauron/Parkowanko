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
        if not parking_point.has_edit_location_proposal:
            parking_point.has_edit_location_proposal = True
            parking_point.save(update_fields=["has_edit_location_proposal"])


@receiver(post_save, sender=ParkingPointEditLocationVote)
def apply_vote_effect(sender, instance, created, **kwargs):
    """
    Automatyczna logika głosowania:
    - jeśli like - dislike >= 3 → zmiana lokalizacji w ParkingPoint
    - jeśli dislike - like >= 3 → usunięcie propozycji
    """

    if not created:
        return  # liczy się tylko pierwszy zapis głosu

    proposal = instance.parking_point_edit_location

    # Liczymy ponownie głosy (żeby uniknąć edge-case)
    likes = ParkingPointEditLocationVote.objects.filter(
        parking_point_edit_location=proposal,
        is_like=True,
    ).count()

    dislikes = ParkingPointEditLocationVote.objects.filter(
        parking_point_edit_location=proposal,
        is_like=False,
    ).count()

    # Aktualizujemy liczniki
    proposal.like_count = likes
    proposal.dislike_count = dislikes
    proposal.save(update_fields=["like_count", "dislike_count"])

    # --- LOGIKA DECYZYJNA ---
    pp = proposal.parking_point
    # ✔️ 3 like więcej → zatwierdzenie zmiany
    # 1️⃣ decyzja o lokalizacji
    if likes - dislikes >= 3:
        pp.location = proposal.location
        proposal.delete()
    elif dislikes - likes >= 3:
        proposal.delete()

    # 2️⃣ aktualizacja flagi w osobnym bloku
    pp.has_edit_location_proposal = ParkingPointEditLocation.objects.filter(
        parking_point=pp
    ).exists()
    pp.save(update_fields=["location", "has_edit_location_proposal"])
