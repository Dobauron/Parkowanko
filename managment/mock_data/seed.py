from .auth import create_users
from .parking_points import create_parking_points
from .pp_edit_locations import create_edit_locations
from .pp_edit_location_vote import create_edit_location_votes


def seed_all():
    users = create_users()
    parking_points = create_parking_points(users)
    edit_locations = create_edit_locations(users, parking_points)
    create_edit_location_votes(users, edit_locations)

    return {
        "users": users,
        "parking_points": parking_points,
        "edit_locations": edit_locations,
    }
