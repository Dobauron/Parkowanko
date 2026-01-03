from rest_framework import serializers
from ..models import ParkingPointEditLocation
from .validators import validate_distance, validate_location_structure


class ParkingPointEditLocationSerializer(serializers.ModelSerializer):
    parkingPointId = serializers.IntegerField(source="parking_point.id", read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ParkingPointEditLocation
        fields = [
            "id",
            "location",  # JSONField zwracany bezpośrednio
            "parkingPointId",
            "user",
            "created_at",
            "updated_at",
        ]

    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }

    @validate_location_structure()
    @validate_distance(min_distance=40, max_distance=100)
    def validate(self, attrs):
        """
        Kolejność walidacji:
        1. Czy location ma dobrą strukturę
        2. Sprawdza odległość w zakresie 40-100m
        """
        return attrs
