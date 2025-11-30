from rest_framework import serializers
from ..models import ParkingPoint
from .validators import validate_location


class ParkingPointSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

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
                {
                    "error": "Nieprawidłowe dane lokalizacji: 'lat' i 'lng' muszą być liczbami."
                }
            )

        # Walidacja lokalizacji
        validate_location(new_lat, new_lng)

        return attrs

    def to_internal_value(self, data):
        if "location" not in data or not data["location"]:
            raise serializers.ValidationError({"error": "Pole location jest wymagane."})
        return super().to_internal_value(data)
