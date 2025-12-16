from parking_point_edit_location.models import ParkingPointEditLocationVote


def create_edit_location_votes(users, edit_locations):
    """
    Tworzy głosy do propozycji edycji lokalizacji
    """

    votes_data = [
        # 👍 warszawa_edit
        {
            "edit": edit_locations["warszawa_edit"],
            "user": users["bob"],
            "is_like": True,
        },
        {
            "edit": edit_locations["warszawa_edit"],
            "user": users["charlie"],
            "is_like": True,
        },
        {
            "edit": edit_locations["warszawa_edit"],
            "user": users["diana"],
            "is_like": False,
        },
        # 👎 krakow_edit
        {
            "edit": edit_locations["krakow_edit"],
            "user": users["alice"],
            "is_like": False,
        },
        {
            "edit": edit_locations["krakow_edit"],
            "user": users["charlie"],
            "is_like": False,
        },
        # 😐 neutralny głos
        {
            "edit": edit_locations["krakow_edit"],
            "user": users["eve"],
            "is_like": None,
        },
    ]

    for vote in votes_data:
        ParkingPointEditLocationVote.objects.get_or_create(
            parking_point_edit_location=vote["edit"],
            user=vote["user"],
            defaults={"is_like": vote["is_like"]},
        )

    # 🔁 aktualizacja liczników
    for edit in edit_locations.values():
        edit.like_count = edit.votes.filter(is_like=True).count()
        edit.dislike_count = edit.votes.filter(is_like=False).count()
        edit.save(update_fields=["like_count", "dislike_count"])
