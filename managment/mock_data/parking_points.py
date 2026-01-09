from parking_point.models import ParkingPoint


def create_parking_points(users):
    """
    Tworzy ParkingPointy z przykładowymi lokalizacjami.
    original_location = prawda bazowa
    current_location = None (do czasu pierwszego konsensusu)
    """

    parking_points_data = [
        {
            "key": "warszawa_centrum",
            "user": users["alice"],
            "original_location": {"lat": 52.22977, "lng": 21.01178},
            "address": "Warszawa, Centrum",
        },
        {
            "key": "krakow_rynek",
            "user": users["bob"],
            "original_location": {"lat": 50.06143, "lng": 19.93658},
            "address": "Kraków, Rynek Główny",
        },
        {
            "key": "gdansk_molo",
            "user": users["charlie"],
            "original_location": {"lat": 54.44469, "lng": 18.56722},
            "address": "Gdańsk, Molo",
        },
        {
            "key": "poznan_stare_miasto",
            "user": users["diana"],
            "original_location": {"lat": 52.40828, "lng": 16.93352},
            "address": "Poznań, Stare Miasto",
        },
        {
            "key": "wroclaw_rynek",
            "user": users["alice"],
            "original_location": {"lat": 51.10933, "lng": 17.03258},
            "address": "Wrocław, Rynek",
        },
    ]

    created = {}

    for data in parking_points_data:
        pp, _ = ParkingPoint.objects.get_or_create(
            original_location=data["original_location"],
            defaults={
                "user": data["user"],
                "address": data["address"],
                "current_location": None,  # start rundy
            },
        )
        created[data["key"]] = pp

    return created
