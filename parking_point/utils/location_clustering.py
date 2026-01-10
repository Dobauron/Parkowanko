import numpy as np
from parking_point.api.validators import haversine
from parking_point_edit_location.models import ParkingPointEditLocation


def cluster_suggestions_by_distance(suggestions, max_distance=25):
    """
    Grupuje zgłoszenia w klastry na podstawie odległości.
    """
    clusters = []

    for suggestion in suggestions:
        placed = False
        lat1, lng1 = suggestion.location["lat"], suggestion.location["lng"]

        for cluster in clusters:
            for other in cluster:
                lat2, lng2 = other.location["lat"], other.location["lng"]
                if haversine(lat1, lng1, lat2, lng2) <= max_distance:
                    cluster.append(suggestion)
                    placed = True
                    break
            if placed:
                break

        if not placed:
            clusters.append([suggestion])

    return clusters


def median_location_for_cluster(cluster):
    """
    Liczy medianę współrzędnych dla klastra.
    """
    lats = [s.location["lat"] for s in cluster]
    lngs = [s.location["lng"] for s in cluster]
    return {
        "lat": float(np.median(lats)),
        "lng": float(np.median(lngs)),
    }


def update_parking_point_location(parking_point):
    suggestions = list(parking_point.location_edits.all())

    if len(suggestions) < 3:
        return  # za mało danych, nic nie robimy

    clusters = cluster_suggestions_by_distance(suggestions, max_distance=25)

    valid_clusters = [c for c in clusters if len(set(s.user_id for s in c)) >= 3]

    if not valid_clusters:
        return

    valid_clusters.sort(key=len, reverse=True)

    # opcjonalnie: sprawdzanie przewagi
    if len(valid_clusters) > 1 and len(valid_clusters[0]) == len(valid_clusters[1]):
        return

    top_cluster = valid_clusters[0]
    new_location = median_location_for_cluster(top_cluster)

    # 1. zapis nowej lokalizacji
    parking_point.location = new_location
    parking_point.save(update_fields=["location"])

    # 2. RESET zgłoszeń
    ParkingPointEditLocation.objects.filter(parking_point=parking_point).delete()
