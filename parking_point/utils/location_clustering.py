import numpy as np
from parking_point.api.validators import haversine


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
    """
    Aktualizuje current_location ParkingPoint na podstawie zgłoszeń użytkowników.
    Jeśli brak konsensusu, używa original_location.
    """
    suggestions = list(parking_point.location_edits.all())

    # fallback – brak zgłoszeń → użyj original_location
    if not suggestions:
        parking_point.current_location = parking_point.original_location
        parking_point.save(update_fields=["current_location"])
        return

    # grupowanie zgłoszeń w klastry
    clusters = cluster_suggestions_by_distance(suggestions, max_distance=25)

    # wybieramy tylko klastry z min. 3 różnymi użytkownikami
    valid_clusters = [c for c in clusters if len(set(s.user_id for s in c)) >= 3]

    # brak klastra spełniającego próg → używamy original_location
    if not valid_clusters:
        parking_point.current_location = parking_point.original_location
        parking_point.save(update_fields=["current_location"])
        return

    # klaster z największą liczbą zgłoszeń
    valid_clusters.sort(key=len, reverse=True)
    top_cluster = valid_clusters[0]

    # ustawiamy current_location w medianie klastra
    parking_point.current_location = median_location_for_cluster(top_cluster)
    parking_point.save(update_fields=["current_location"])
