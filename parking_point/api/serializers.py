from rest_framework import serializers
from .validators import (
    reject_invalid_location_structure,
    reject_too_close_to_other_points,
)
from ..models import ParkingPoint


class ParkingPointSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = ParkingPoint
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "user",
            "like_count",
            "dislike_count",
        )

    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }

    def get_like_count(self, obj):
        return getattr(obj, "like_count", 0)

    def get_dislike_count(self, obj):
        return getattr(obj, "dislike_count", 0)

    @reject_invalid_location_structure
    @reject_too_close_to_other_points(distance_limit=40)
    def validate_location(self, location):
        return location
