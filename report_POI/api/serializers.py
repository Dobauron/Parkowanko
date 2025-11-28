from rest_framework import serializers
from ..models import ParkingPointReport
from .validators import validate_reason


class ParkingPointReportSerializer(serializers.ModelSerializer):
    reason = serializers.ChoiceField(
        choices=ParkingPointReport.ReportReason.choices, validators=[validate_reason]
    )

    class Meta:
        model = ParkingPointReport
        fields = ["id", "parking_points", "reason", "description", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Jeśli powód to "other", opis nie może być pusty
        if attrs.get(
            "reason"
        ) == ParkingPointReport.ReportReason.OTHER and not attrs.get("description"):
            raise serializers.ValidationError(
                {"error": "Opis jest wymagany dla powodu 'Inne'."}
            )
        return attrs
