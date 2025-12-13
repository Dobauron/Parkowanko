from reviews.models import Review


def create_reviews(users, parking_points):
    """
    users: dict z create_users()
    parking_points: dict z create_parking_points()
    """

    reviews_data = [
        # 👍 pozytywne
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

        # 👎 negatywne
        {
            "user": users["diana"],
            "parking_point": parking_points["krakow_rynek"],
            "is_like": False,
            "description": "Zawsze zajęte.",
        },

        # 😐 neutralne
        {
            "user": users["eve"],
            "parking_point": parking_points["krakow_rynek"],
            "is_like": None,
            "description": "Ciężko ocenić, różnie bywa.",
        },

        # 👍 mieszane
        {
            "user": users["alice"],
            "parking_point": parking_points["gdansk_molo"],
            "is_like": True,
            "description": "Blisko morza, super miejscówka.",
        },
    ]

    created = []

    for data in reviews_data:
        review, created_flag = Review.objects.get_or_create(
            user=data["user"],
            parking_point=data["parking_point"],
            defaults={
                "is_like": data["is_like"],
                "description": data["description"],
            },
        )
        created.append(review)

    return created
