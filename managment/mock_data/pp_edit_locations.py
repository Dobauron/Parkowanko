from parking_point_edit_location.models import ParkingPointEditLocation


def create_edit_locations(users, parking_points):
    """
    Tworzy propozycje edycji lokalizacji ParkingPoint.
    Jeśli użytkownik już ma propozycję dla danego parking_point, nadpisuje ją.
    """

    edit_locations_data = [
        {
            "key": "warszawa_edit",
            "user": users["alice"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.2305, "lng": 21.0115},
        },
        {
            "key": "krakow_edit",
            "user": users["bob"],
            "parking_point": parking_points["krakow_rynek"],
            "location": {"lat": 50.0618, "lng": 19.9372},
        },
    ]

    created_edits = {}

    for data in edit_locations_data:
        # jeśli istnieje → nadpisz location
        edit, created = ParkingPointEditLocation.objects.update_or_create(
            user=data["user"],
            parking_point=data["parking_point"],
            defaults={"location": data["location"]},
        )
        created_edits[data["key"]] = edit

    return created_edits
