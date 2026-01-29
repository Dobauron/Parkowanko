from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from parking_point.models import ParkingPoint
from parking_point.utils.clean_up import cleanup_foreign_edit_points
from django.utils import timezone
from django.db.models import Count, Q
from Reviews.models import (
    Review,
)  # Upewnij się, że ścieżka do modelu Review jest poprawna


@receiver(post_save, sender=ParkingPoint)
def cleanup_on_create(sender, instance, created, **kwargs):
    if created:
        cleanup_foreign_edit_points(instance)


@receiver([post_save, post_delete], sender=Review)
def update_parking_point_deletion_status(sender, instance, **kwargs):
    """
    Sygnał reaguje na każdą nową, zmienioną lub usuniętą recenzję.
    """
    parking_point = instance.parking_point

    # 1. Agregujemy lajki i dislajki dla tego konkretnego punktu
    stats = parking_point.reviews.aggregate(
        likes=Count("id", filter=Q(is_like=True)),
        dislikes=Count("id", filter=Q(is_like=False)),
    )

    likes = stats["likes"] or 0
    dislikes = stats["dislikes"] or 0

    # 2. Sprawdzamy warunek: Dislike - Like >= 5
    if (dislikes - likes) >= 5:
        # Jeśli warunek spełniony, a stoper jeszcze nie ruszył - ustawiamy datę
        if not parking_point.marked_for_deletion_at:
            parking_point.marked_for_deletion_at = timezone.now()
            parking_point.save(update_fields=["marked_for_deletion_at"])
    else:
        # Jeśli bilans się poprawił (np. ktoś dodał lajka lub usunął dislajka)
        # i stoper był włączony - resetujemy go (wybaczamy)
        if parking_point.marked_for_deletion_at:
            parking_point.marked_for_deletion_at = None
            parking_point.save(update_fields=["marked_for_deletion_at"])
