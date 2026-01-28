from parking_point_edit_location.models import ParkingPointEditLocation


def create_edit_locations(users, parking_points):
    """
    Tworzy propozycje edycji lokalizacji ParkingPoint.

    Zawiera:
    - klaster ważny (3 zgłoszenia blisko siebie)
    - klaster za mały (2 zgłoszenia)
    - pojedyncze zgłoszenia dla innych punktów

    Idealne do testów:
    - konsensusu
    - fallbacku
    - resetu rundy
    """

    edit_locations_data = [
        # ----------------------------
        # WARSZAWA – KLASTER
        # ----------------------------
        {
            "key": "wawa_c1_u1",
            "user": users["alice"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.23050, "lng": 21.01150},
        },
        {
            "key": "wawa_c1_u2",
            "user": users["bob"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.23051, "lng": 21.01151},
        },
        # ---------------------------------
        # WARSZAWA – KLASTER ZA MAŁY (2)
        # ---------------------------------
        {
            "key": "wawa_c2_u1",
            "user": users["diana"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.23100, "lng": 21.01200},
        },
        {
            "key": "wawa_c2_u2",
            "user": users["eve"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.23101, "lng": 21.01201},
        },
        # ----------------------------
        # INNE PARKINGI – LUŹNE
        # ----------------------------
        {
            "key": "krakow_edit",
            "user": users["alice"],
            "parking_point": parking_points["krakow_rynek"],
            "location": {"lat": 50.0618, "lng": 19.9372},
        },
        {
            "key": "gdansk_edit",
            "user": users["bob"],
            "parking_point": parking_points["gdansk_molo"],
            "location": {"lat": 54.4447, "lng": 18.5672},
        },
        {
            "key": "wroclaw_edit",
            "user": users["alice"],
            "parking_point": parking_points["wroclaw_rynek"],
            "location": {"lat": 51.1095, "lng": 17.0327},
        },
    ]

    created = {}

    for data in edit_locations_data:
        edit, _ = ParkingPointEditLocation.objects.update_or_create(
            user=data["user"],
            parking_point=data["parking_point"],
            defaults={"location": data["location"]},
        )
        created[data["key"]] = edit

    return created
