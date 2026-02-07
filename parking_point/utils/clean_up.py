from parking_point.utils.geo_utils import haversine
from parking_point_edit_location.models import ParkingPointEditLocation

CLEANUP_RADIUS_METERS = 25


def cleanup_foreign_edit_points(parking_point, radius=CLEANUP_RADIUS_METERS):
    """
    Usuwa edit_location innych ParkingPointów,
    które znajdują się w obszarze tego ParkingPoint.
    """

    if not parking_point.location:
        return

    lat1 = parking_point.location["lat"]
    lng1 = parking_point.location["lng"]

    edits = ParkingPointEditLocation.objects.exclude(
        parking_point=parking_point
    ).select_related("parking_point")

    to_delete = []

    for edit in edits:
        lat2 = edit.location["lat"]
        lng2 = edit.location["lng"]

        if haversine(lat1, lng1, lat2, lng2) <= radius:
            to_delete.append(edit.id)

    if to_delete:
        ParkingPointEditLocation.objects.filter(id__in=to_delete).delete()
