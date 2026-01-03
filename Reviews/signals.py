from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Q
from .models import Review


@receiver(post_save, sender=Review)
def verify_parking_point_on_votes(sender, instance, created, **kwargs):
    """
    ParkingPoint zostaje zweryfikowany, gdy:
    liczba like - liczba dislike >= 3
    """
    if not created:
        return

    parking_point = instance.parking_point

    aggregates = Review.objects.filter(
        parking_point=parking_point,
        is_like__isnull=False,
    ).aggregate(
        likes=Count("id", filter=Q(is_like=True)),
        dislikes=Count("id", filter=Q(is_like=False)),
    )

    likes = aggregates["likes"] or 0
    dislikes = aggregates["dislikes"] or 0

    if likes - dislikes >= 3 and not parking_point.is_verified:
        parking_point.is_verified = True
        parking_point.save(update_fields=["is_verified"])
