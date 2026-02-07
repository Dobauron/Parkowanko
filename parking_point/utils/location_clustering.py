import numpy as np
import logging

from django.conf import settings
from django.db import transaction

from parking_point_edit_location.models import ParkingPointEditLocation
from .geo_utils import haversine


logger = logging.getLogger(__name__)


# ============================================================
#  KONFIGURACJA (możliwa do nadpisania w settings.py)
# ============================================================

DEFAULT_CLUSTER_CONFIG = {
    "MIN_USERS_IN_CLUSTER": 3,  # minimalna liczba unikalnych userów w klastrze
    "CLUSTER_RADIUS_METERS": 25,  # promień klastra
    "REQUIRE_ADVANTAGE": True,  # czy wymagamy przewagi nad drugim klastrem
}


def get_cluster_config():
    return getattr(settings, "PARKING_POINT_CLUSTERING", DEFAULT_CLUSTER_CONFIG)


# ============================================================
#  KLASTERYZACJA
# ============================================================


def cluster_suggestions_by_distance(suggestions, max_distance):
    """
    Grupuje zgłoszenia w klastry na podstawie odległości (haversine).
    Każde zgłoszenie trafia do pierwszego klastra,
    w którym znajdzie punkt w promieniu max_distance.
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


# ============================================================
#  GŁÓWNA FUNKCJA BIZNESOWA
# ============================================================


def update_parking_point_location(parking_point):
    """
    Główna logika zatwierdzania klastra.

    Warunki:
    - musi istnieć klaster z min. liczbą unikalnych userów
    - opcjonalnie: musi mieć przewagę nad drugim klastrem

    Efekt:
    - location ParkingPoint = mediana klastra
    - wszystkie edit_location dla tego PP są usuwane
    """

    cfg = get_cluster_config()

    with transaction.atomic():
        # blokada wierszy – ochrona przed race condition
        suggestions = list(parking_point.location_edits.select_for_update())

        if len(suggestions) < cfg["MIN_USERS_IN_CLUSTER"]:
            return

        clusters = cluster_suggestions_by_distance(
            suggestions,
            max_distance=cfg["CLUSTER_RADIUS_METERS"],
        )

        valid_clusters = [
            c
            for c in clusters
            if len(set(s.user_id for s in c)) >= cfg["MIN_USERS_IN_CLUSTER"]
        ]

        if not valid_clusters:
            return

        valid_clusters.sort(key=len, reverse=True)

        # jeżeli wymagamy przewagi – blokujemy remis
        if cfg["REQUIRE_ADVANTAGE"] and len(valid_clusters) > 1:
            if len(valid_clusters[0]) == len(valid_clusters[1]):
                return

        top_cluster = valid_clusters[0]
        new_location = median_location_for_cluster(top_cluster)

        # zapis nowej lokalizacji
        parking_point.location = new_location
        parking_point.save(update_fields=["location"])

        # usunięcie editów z klastra po zatwierdzeniu
        deleted_count = parking_point.location_edits.all().delete()

        logger.info(
            "Cluster approved | PP=%s | location=%s | Removed edits: %s",
            parking_point.id,
            new_location,
            deleted_count,
        )
