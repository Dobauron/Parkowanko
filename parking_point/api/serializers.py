from rest_framework import serializers
from .validators import (
    reject_invalid_location_structure,
    reject_too_close_to_other_points,
)
from ..models import ParkingPoint


class ParkingPointSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    like_count = serializers.IntegerField(read_only=True)
    dislike_count = serializers.IntegerField(read_only=True)

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
            "like_count",
            "dislike_count",
        )

    @reject_invalid_location_structure
    @reject_too_close_to_other_points(distance_limit=40)
    def validate_location(self, location):
        return location

    # zwraca pola like i dislike w metodzie POST
    def create(self, validated_data):
        instance = super().create(validated_data)

        # wstrzykujemy brakujące pola
        instance.like_count = 0
        instance.dislike_count = 0

        return instance
