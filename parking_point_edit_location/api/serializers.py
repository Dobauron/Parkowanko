from rest_framework import serializers
from ..models import ParkingPointEditLocation, ParkingPointEditLocationVote
from .validators import (
    validate_distance,
    validate_no_existing_proposal,
    validate_location_structure,
    validate_has_proposal,
    validate_proposal_exists,
    validate_user_not_voted,
)


class ParkingPointEditLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParkingPointEditLocation
        fields = ["id", "location"]
        read_only_fields = ["id"]

    @validate_location_structure()
    @validate_no_existing_proposal()
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


class ParkingPointEditLocationVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingPointEditLocationVote
        fields = ["is_like"]

    @validate_has_proposal()
    @validate_proposal_exists()
    @validate_user_not_voted()
    def validate(self, attrs):
        """
        Wszystkie walidacje są w dekoratorach
        """
        # Tutaj możesz dodać dodatkowe walidacje jeśli potrzebujesz
        # np. sprawdzenie czy is_like jest bool
        is_like = attrs.get("is_like")
        if not isinstance(is_like, bool):
            raise serializers.ValidationError({"is_like": "Musi być true lub false."})

        return attrs
