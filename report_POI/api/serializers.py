from rest_framework import serializers
from ..models import ParkingPointReport
from .validators import validate_reason


class ParkingPointReportSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(
        validators=[validate_reason]
    )  # Dodajemy walidator do pola

    class Meta:
        model = ParkingPointReport
        fields = ["id", "user", "parking_point", "reason", "description", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate(self, attrs):
        # Jeśli powód to "other", opis nie może być pusty
        if attrs.get(
            "reason"
        ) == ParkingPointReport.ReportReason.OTHER and not attrs.get("description"):
            raise serializers.ValidationError(
                {"error": "Opis jest wymagany dla powodu 'Inne'."}
            )
        return attrs
