from rest_framework import serializers
from ..models import ParkingPoint
from .validators import validate_location


class ParkingPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingPoint
        fields = "__all__"

    def validate(self, attrs):
        # Pobierz dane lokalizacji
        try:
            new_lat = float(attrs["location"]["lat"])
            new_lng = float(attrs["location"]["lng"])
        except (KeyError, ValueError):
            raise serializers.ValidationError(
                "Nieprawidłowe dane lokalizacji: 'lat' i 'lng' muszą być liczbami."
            )

        # Walidacja lokalizacji
        validate_location(new_lat, new_lng)

        return attrs

    def validate_location(self, value):
        if not value:
            raise serializers.ValidationError("Pole location jest wymagane.")
        return value