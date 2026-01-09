from Reviews.models import Review


def create_reviews(users, parking_points):
    """
    Tworzy przykładowe recenzje ParkingPoint.
    users: dict z Account
    parking_points: dict z ParkingPoint
    """
    reviews_data = [
        # pozytywne
        {
            "user": users["bob"],
            "parking_point": parking_points["warszawa_centrum"],
            "is_like": True,
            "description": "Dużo miejsc, dobra lokalizacja.",
        },
        {
            "user": users["charlie"],
            "parking_point": parking_points["warszawa_centrum"],
            "is_like": True,
            "description": "Bez problemu zaparkowałem.",
        },
        # negatywne
        {
            "user": users["diana"],
            "parking_point": parking_points["krakow_rynek"],
            "is_like": False,
            "description": "Zawsze zajęte.",
        },
        {
            "user": users["eve"],
            "parking_point": parking_points["krakow_rynek"],
            "is_like": False,
            "description": "Ciężko ocenić, różnie bywa.",
        },
        # mieszane / pozytywne
        {
            "user": users["alice"],
            "parking_point": parking_points["gdansk_molo"],
            "is_like": True,
            "description": "Blisko morza, super miejscówka.",
        },
        {
            "user": users["bob"],
            "parking_point": parking_points["gdansk_molo"],
            "is_like": True,
            "description": "Blisko morza, super miejscówka.",
        },
        {
            "user": users["diana"],
            "parking_point": parking_points["warszawa_centrum"],
            "is_like": True,
            "description": "Blisko morza, super miejscówka.",
        },
    ]

    created = []

    for data in reviews_data:
        review, _ = Review.objects.get_or_create(
            user=data["user"],
            parking_point=data["parking_point"],
            defaults={
                "is_like": data["is_like"],
                "description": data["description"],
            },
        )
        created.append(review)

    return created
