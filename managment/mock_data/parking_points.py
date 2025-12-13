from parking_point.models import ParkingPoint


def create_parking_points(users):
    parking_points_data = [
        {
            "key": "warszawa_centrum",
            "user": users["alice"],
            "location": {"lat": 52.22977, "lng": 21.01178},
            "is_verified": True,
        },
        {
            "key": "krakow_rynek",
            "user": users["bob"],
            "location": {"lat": 50.06143, "lng": 19.93658},
            "is_verified": True,
        },
        {
            "key": "gdansk_molo",
            "user": users["charlie"],
            "location": {"lat": 54.44469, "lng": 18.56722},
            "is_verified": False,
        },
        {
            "key": "poznan_stare_miasto",
            "user": users["diana"],
            "location": {"lat": 52.40828, "lng": 16.93352},
            "is_verified": False,
        },
        {
            "key": "wroclaw_rynek",
            "user": users["alice"],
            "location": {"lat": 51.10933, "lng": 17.03258},
            "is_verified": False,
        },
    ]

    created = {}

    for data in parking_points_data:
        pp, _ = ParkingPoint.objects.get_or_create(
            location=data["location"],
            defaults={
                "user": data["user"],
                "is_verified": data["is_verified"],
                "has_edit_location_proposal": False,
            },
        )
        created[data["key"]] = pp

    return created
