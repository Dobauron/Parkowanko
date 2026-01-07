from parking_point_edit_location.models import ParkingPointEditLocation


def create_edit_locations(users, parking_points):
    """
    Tworzy propozycje edycji lokalizacji ParkingPoint.
    Nadpisuje istniejące zgłoszenie, jeśli użytkownik już zgłosił edycję.

    Dodatkowo dodaje mocki do testowania klastrów:
    - 3 zgłoszenia w pobliżu (klaster ważny)
    - 2 zgłoszenia w pobliżu (za mało, fallback)
    - kilka rozrzuconych zgłoszeń dla innych testów
    """
    edit_locations_data = [
        # Klaster 1 (3 osoby – powinien zmienić pinezkę)
        {
            "key": "warszawa_cluster1_u1",
            "user": users["alice"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.2305, "lng": 21.0115},
        },
        {
            "key": "warszawa_cluster1_u2",
            "user": users["bob"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.23051, "lng": 21.01151},
        },
        {
            "key": "warszawa_cluster1_u3",
            "user": users["charlie"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.23052, "lng": 21.01152},
        },

        # Klaster 2 (2 osoby – za mało, powinien być ignorowany)
        {
            "key": "warszawa_cluster2_u1",
            "user": users["diana"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.231, "lng": 21.012},
        },
        {
            "key": "warszawa_cluster2_u2",
            "user": users["eve"],
            "parking_point": parking_points["warszawa_centrum"],
            "location": {"lat": 52.23101, "lng": 21.01201},
        },

        # Pojedyncze zgłoszenia dla innych parkingów
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
            "location": {"lat": 54.4447, "lng": 18.5672},
        },
    ]

    created_edits = {}

    for data in edit_locations_data:
        edit, _ = ParkingPointEditLocation.objects.update_or_create(
            user=data["user"],
            parking_point=data["parking_point"],
            defaults={"location": data["location"]},
        )
        created_edits[data["key"]] = edit

    return created_edits
