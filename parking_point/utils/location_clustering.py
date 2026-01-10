import numpy as np
import logging
from django.conf import settings
from django.db import transaction
from parking_point_edit_location.models import ParkingPointEditLocation
from parking_point.api.validators import haversine  # Twoja funkcja z validators.py

logger = logging.getLogger(__name__)

# --- KONFIGURACJA DOMYŚLNA ---
DEFAULT_CLUSTER_CONFIG = {
    "MIN_USERS_IN_CLUSTER": 3,
    "CLUSTER_RADIUS_METERS": 25,
    "REQUIRE_ADVANTAGE": True,
}

# ----------------- FUNKCJE -----------------


def cluster_suggestions_by_distance(suggestions, max_distance):
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
    lats = [s.location["lat"] for s in cluster]
    lngs = [s.location["lng"] for s in cluster]
    return {"lat": float(np.median(lats)), "lng": float(np.median(lngs))}


def update_parking_point_location(parking_point):
    cfg = getattr(settings, "PARKING_POINT_CLUSTERING", DEFAULT_CLUSTER_CONFIG)

    with transaction.atomic():
        # blokada wierszy, aby uniknąć race condition
        suggestions = list(parking_point.location_edits.select_for_update())

        if len(suggestions) < cfg["MIN_USERS_IN_CLUSTER"]:
            return  # za mało zgłoszeń w ogóle

        clusters = cluster_suggestions_by_distance(
            suggestions, max_distance=cfg["CLUSTER_RADIUS_METERS"]
        )

        valid_clusters = [
            c
            for c in clusters
            if len(set(s.user_id for s in c)) >= cfg["MIN_USERS_IN_CLUSTER"]
        ]

        if not valid_clusters:
            return  # brak klastra z minimalną liczbą userów

        valid_clusters.sort(key=len, reverse=True)

        # opcjonalnie: sprawdzanie remisu
        if cfg["REQUIRE_ADVANTAGE"] and len(valid_clusters) > 1:
            if len(valid_clusters[0]) == len(valid_clusters[1]):
                return  # remis → brak przesunięcia

        top_cluster = valid_clusters[0]
        new_location = median_location_for_cluster(top_cluster)

        # zapis mediany do pola location
        parking_point.location = new_location
        parking_point.save(update_fields=["location"])

        # usunięcie wszystkich editów po zatwierdzeniu
        ParkingPointEditLocation.objects.filter(parking_point=parking_point).delete()

        # logowanie do monitoringu
        logger.info(
            "Cluster approved for ParkingPoint %s, new location: %s, users: %s",
            parking_point.id,
            new_location,
            [s.user_id for s in top_cluster],
        )
