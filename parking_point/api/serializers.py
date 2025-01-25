from rest_framework import serializers
from ..models import ParkingPoint
import math


class ParkingPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingPoint
        fields = "__all__"

    def validate(self, attrs):
        new_location = attrs.get("location", {})
        try:
            new_lat = float(new_location.get("latitude"))
            new_lon = float(new_location.get("longitude"))
        except (TypeError, ValueError):
            raise serializers.ValidationError("Szerokość i długość geograficzna muszą być liczbami.")

        # Sprawdzenie zakresów latitude i longitude
        if not (-90 <= new_lat <= 90):
            raise serializers.ValidationError("Szerokość geograficzna (latitude) musi być w zakresie od -90 do 90.")
        if not (-180 <= new_lon <= 180):
            raise serializers.ValidationError("Długość geograficzna (longitude) musi być w zakresie od -180 do 180.")

        # Pobierz wszystkie istniejące punkty parkingowe
        existing_points = ParkingPoint.objects.all()

        # Funkcja obliczająca odległość Haversine w metrach
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000  # Promień Ziemi w metrach
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)

            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            return R * c

        # Sprawdź odległość dla każdego istniejącego punktu
        for point in existing_points:
            existing_location = point.location
            try:
                existing_lat = float(existing_location.get("latitude"))
                existing_lon = float(existing_location.get("longitude"))
            except (TypeError, ValueError):
                continue  # Pomijamy punkty z niepełnymi danymi

            distance = haversine(new_lat, new_lon, existing_lat, existing_lon)
            if distance < 100:  # Jeśli odległość jest mniejsza niż 100 metrów, zwróć błąd
                raise serializers.ValidationError(
                    f"Nowy punkt znajduje się zbyt blisko istniejącego punktu: {point.name} ({distance:.2f}m odległości)."
                )

        return attrs
