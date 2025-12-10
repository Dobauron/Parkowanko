from rest_framework import serializers
from .validators import (
    reject_invalid_location_structure,
    reject_water_locations,
    reject_too_close_to_other_points
)
from ..models import ParkingPoint


class ParkingPointSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ParkingPoint
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_verified",
            "user",
            "has_edit_location_proposal",
        )

    @reject_invalid_location_structure
    @reject_water_locations
    @reject_too_close_to_other_points(distance_limit=40)
    def validate_location(self, location):
        return location
