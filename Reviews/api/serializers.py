from rest_framework import serializers
from ..models import Review
from .validators import validate_property, validate_occupancy


class ReviewSerializer(serializers.ModelSerializer):
    properties = serializers.ListField(
        child=serializers.CharField(validators=[validate_property]),
        required=False,
        allow_empty=True,  # <- pozwala na pustą listę
        default=list
    )

    occupancy = serializers.CharField(
        validators=[validate_occupancy],
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "parking_point",
            "properties",
            "occupancy",
            "is_liked",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Jeśli użytkownik wybrał OTHER, opis musi być uzupełniony
        properties = attrs.get("properties", [])
        if "OTHER" in properties and not attrs.get("description"):
            raise serializers.ValidationError({
                "description": "Opis jest wymagany, gdy wybrano 'Inne'."
            })

        return attrs
