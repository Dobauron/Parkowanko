from django.utils import timezone
from datetime import timedelta
from parking_point.models import ParkingPoint


def create_parking_points(users):
    """
    Tworzy ParkingPointy z przykładowymi lokalizacjami oraz punkt testowy do usuwania.
    """
    now = timezone.now()

    parking_points_data = [
        {
            "key": "warszawa_centrum",
            "user": users["alice"],
            "location": {"lat": 52.22977, "lng": 21.01178},
            "address": "Warszawa, Centrum",
            "marked_for_deletion_at": None,
        },
        {
            "key": "krakow_rynek",
            "user": users["bob"],
            "location": {"lat": 50.06143, "lng": 19.93658},
            "address": "Kraków, Rynek Główny",
            "marked_for_deletion_at": None,
        },
        {
            "key": "gdansk_molo",
            "user": users["charlie"],
            "location": {"lat": 54.44469, "lng": 18.56722},
            "address": "Gdańsk, Molo",
            "marked_for_deletion_at": None,
        },
        {
            "key": "poznan_stare_miasto",
            "user": users["diana"],
            "location": {"lat": 52.40828, "lng": 16.93352},
            "address": "Poznań, Stare Miasto",
            "marked_for_deletion_at": None,
        },
        {
            "key": "wroclaw_rynek",
            "user": users["alice"],
            "location": {"lat": 51.10933, "lng": 17.03258},
            "address": "Wrocław, Rynek",
            "marked_for_deletion_at": None,
        },
        # --- PUNKT TESTOWY: ZNIKNIE PO 1 MINUCIE ---
        {
            "key": "znikajacy_punkt",
            "user": users["bob"],
            "location": {"lat": 52.00000, "lng": 21.00000},
            "address": "Test usuwania (zniknę po minucie)",
            # Ustawiamy czas tak, by do 30 dni brakowało mu tylko 60 sekund:
            "marked_for_deletion_at": now - timedelta(days=30) + timedelta(seconds=60),
        },
    ]

    created = {}

    for data in parking_points_data:
        # Pamiętaj, aby dodać marked_for_deletion_at do defaults
        pp, _ = ParkingPoint.objects.update_or_create(
            address=data["address"],
            defaults={
                "user": data["user"],
                "location": data["location"],
                "marked_for_deletion_at": data.get("marked_for_deletion_at"),
            },
        )
        created[data["key"]] = pp

    return created


# W Twoim skrypcie seedującym (np. reviews.py)
def create_test_reviews(users, parking_points):
    target_pp = parking_points["wroclaw_rynek"]

    # Dodajemy 5 dislajków od różnych userów
    for i in range(5):
        Review.objects.create(
            user=list(users.values())[i],
            parking_point=target_pp,
            is_like=False,
        )
