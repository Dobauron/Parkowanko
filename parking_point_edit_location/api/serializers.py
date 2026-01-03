from rest_framework import serializers
from ..models import ParkingPointEditLocation
from .validators import (
    validate_distance,
    validate_location_structure,
)


class ParkingPointEditLocationSerializer(serializers.ModelSerializer):
    parkingPointId = serializers.IntegerField(source="parking_point.id", read_only=True)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        model = ParkingPointEditLocation
        fields = [
            "id",
            "location",  # JSONField zwracany bezpośrednio
            "parkingPointId",
            "like_count",
            "dislike_count",
        ]

    def get_like_count(self, obj) -> int:
        return obj.votes.filter(is_like=True).count()

    def get_dislike_count(self, obj) -> int:
        return obj.votes.filter(is_like=False).count()

    @validate_location_structure()
    @validate_distance(min_distance=20, max_distance=100)
    def validate(self, attrs):
        """
        Kolejność walidacji:
        1. Czy location ma dobrą strukturę
        2. Sprawdza has_proposal
        3. Czy odległość jest w zakresie 20-100m
        """
        # Tutaj możesz dodać inne walidacje jeśli potrzebujesz
        return attrs


