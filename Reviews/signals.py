from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review
from parking_point.models import ParkingPoint

@receiver(post_save, sender=Review)
def verify_parking_point_on_likes(sender, instance, created, **kwargs):
    """
    Jeżeli parking point ma >=2 recenzje z is_like=True
    oznacz go jako zweryfikowany.
    """
    if not created:
        return  # interesuje nas tylko tworzenie nowych recenzji

    parking_point = instance.parking_point

    # Policz pozytywne recenzje
    like_count = Review.objects.filter(
        parking_point=parking_point,
        is_like=True
    ).count()

    if like_count >= 2 and not parking_point.is_verified:
        parking_point.is_verified = True
        parking_point.save(update_fields=["is_verified"])
