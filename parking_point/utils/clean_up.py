from django.contrib.gis.measure import D # Import D (Distance)
from django.contrib.gis.db.models.functions import Distance
from parking_point_edit_location.models import ParkingPointEditLocation

CLEANUP_RADIUS_METERS = 25


def cleanup_foreign_edit_points(parking_point, radius=CLEANUP_RADIUS_METERS):
    """
    Usuwa edit_location innych ParkingPointów,
    które znajdują się w obszarze tego ParkingPoint.
    """

    if not parking_point.location:
        return

    # PostGIS robi to jedną, szybką komendą!
    ParkingPointEditLocation.objects.exclude(
        parking_point=parking_point
    ).filter(
        location__distance_lte=(parking_point.location, D(m=radius))
    ).delete()
