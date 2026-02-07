from Reviews.models import Review


def create_reviews(users, parking_points):
    """
    Tworzy bogate w dane recenzje z atrybutami i statusem obłożenia.
    """
    reviews_data = [
        # WARSZAWA - Mix opinii
        {
            "user": users["bob"],
            "parking_point": parking_points["warszawa_centrum"],
            "is_like": True,
            "occupancy": Review.Occupancy.HIGH,
            "attributes": [Review.Attributes.POOR_LIGHTING],
            "description": "Ciasno, ale w samym centrum.",
        },
        {
            "user": users["charlie"],
            "parking_point": parking_points["warszawa_centrum"],
            "is_like": False,
            "occupancy": Review.Occupancy.NO_SPACE,
            "attributes": [Review.Attributes.PARKING_RESTRICTIONS],
            "description": "Tylko dla mieszkańców w godzinach szczytu.",
        },
        # KRAKÓW - Dramatyczna nawierzchnia
        {
            "user": users["diana"],
            "parking_point": parking_points["krakow_rynek"],
            "is_like": False,
            "occupancy": Review.Occupancy.MEDIUM,
            "attributes": [
                Review.Attributes.POOR_SURFACE,
                Review.Attributes.HARD_ACCESS,
            ],
            "description": "Dziury jak po bombardowaniu, nie polecam niskim autom.",
        },
        # GDAŃSK - Pozytyw, ale podtapia
        {
            "user": users["alice"],
            "parking_point": parking_points["gdansk_molo"],
            "is_like": True,
            "occupancy": Review.Occupancy.LOW,
            "attributes": [
                Review.Attributes.FLOOD_PRONE,
                Review.Attributes.FREE_OFF_SEASON,
            ],
            "description": "Super poza sezonem, ale przy deszczu stoi woda.",
        },
        # POZNAŃ - Bezpieczeństwo
        {
            "user": users["eve"],
            "parking_point": parking_points["poznan_stare_miasto"],
            "is_like": False,
            "occupancy": Review.Occupancy.HIGH,
            "attributes": [Review.Attributes.DANGEROUS_AREA],
            "description": "Strach zostawić auto po zmroku.",
        },
    ]

    # TEST SCENARIO: WROCŁAW (Punkt widmo / Do usunięcia)
    # 5 osób zgłasza brak miejsca i tragiczne warunki
    wroclaw = parking_points["wroclaw_rynek"]
    test_usernames = ["alice", "bob", "charlie", "diana", "eve"]

    for username in test_usernames:
        reviews_data.append(
            {
                "user": users[username],
                "parking_point": wroclaw,
                "is_like": False,
                "occupancy": Review.Occupancy.NO_DATA,
                "attributes": [Review.Attributes.HARD_ACCESS],
                "description": "To miejsce jest zagrodzone słupkami!",
            }
        )

    created = []
    for data in reviews_data:
        review, _ = Review.objects.update_or_create(
            user=data["user"],
            parking_point=data["parking_point"],
            defaults={
                "is_like": data["is_like"],
                "occupancy": data.get("occupancy", Review.Occupancy.NO_DATA),
                "attributes": data.get("attributes", []),
                "description": data.get("description", ""),
            },
        )
        created.append(review)
    return created
