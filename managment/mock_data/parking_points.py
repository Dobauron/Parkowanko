from parking_point.models import ParkingPoint


def create_parking_points(users):
    """
    Tworzy ParkingPointy z przykładowymi lokalizacjami.

    Zasady:
    - original_location = prawda bazowa (pierwsza lokalizacja)
    - location = aktualna lokalizacja (na starcie = original_location)
    """

    parking_points_data = [
        {
            "key": "warszawa_centrum",
            "user": users["alice"],
            "location": {"lat": 52.22977, "lng": 21.01178},
            "address": "Warszawa, Centrum",
        },
        {
            "key": "krakow_rynek",
            "user": users["bob"],
            "location": {"lat": 50.06143, "lng": 19.93658},
            "address": "Kraków, Rynek Główny",
        },
        {
            "key": "gdansk_molo",
            "user": users["charlie"],
            "location": {"lat": 54.44469, "lng": 18.56722},
            "address": "Gdańsk, Molo",
        },
        {
            "key": "poznan_stare_miasto",
            "user": users["diana"],
            "location": {"lat": 52.40828, "lng": 16.93352},
            "address": "Poznań, Stare Miasto",
        },
        {
            "key": "wroclaw_rynek",
            "user": users["alice"],
            "location": {"lat": 51.10933, "lng": 17.03258},
            "address": "Wrocław, Rynek",
        },
    ]

    created = {}

    for data in parking_points_data:
        pp, _ = ParkingPoint.objects.get_or_create(
            address=data["address"],
            defaults={
                "user": data["user"],
                "address": data["address"],
                "location": data["location"],
            },
        )
        created[data["key"]] = pp

    return created
