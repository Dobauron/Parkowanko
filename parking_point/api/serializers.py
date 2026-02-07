from rest_framework import serializers
from .validators import (
    reject_invalid_location_structure,
)
from ..models import ParkingPoint
from drf_spectacular.utils import extend_schema_field


class ParkingPointSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = ParkingPoint
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "user",
            "like_count",
            "dislike_count",
        )
        exclude = ["original_location", "marked_for_deletion_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        location = validated_data.get("location")

        parking_point = ParkingPoint.objects.create(
            user=request.user if request else None,
            original_location=location,
            location=location,
            address=validated_data.get("address"),
        )

        return parking_point

    @extend_schema_field(serializers.DictField)
    def get_user(self, obj):
        # Sprawdzamy, czy parking ma przypisanego użytkownika
        if obj.user:
            return {
                "id": obj.user.id,
                "username": obj.user.username,
            }
        # Jeśli nie ma użytkownika (np. po imporcie), zwracamy info o systemie lub None
        return {
            "id": None,
            "username": "System/Import",
        }

    @extend_schema_field(serializers.IntegerField)
    def get_like_count(self, obj):
        return getattr(obj, "like_count", 0)

    @extend_schema_field(serializers.IntegerField)
    def get_dislike_count(self, obj):
        return getattr(obj, "dislike_count", 0)

    @reject_invalid_location_structure
    # @reject_too_close_to_other_points(distance_limit=30)
    def validate_location(self, location):
        return location
