from rest_framework import serializers
from ..models import Review
from .validators import validate_attribiutes, validate_occupancy


class ReviewSerializer(serializers.ModelSerializer):
    attribiutes = serializers.ListField(
        child=serializers.CharField(validators=[validate_attribiutes]),
        required=False,
        allow_empty=True,
        default=list,
    )

    occupancy = serializers.CharField(
        validators=[validate_occupancy],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "parking_point",
            "attribiutes",
            "occupancy",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Jeśli użytkownik wybrał OTHER, opis musi być uzupełniony
        properties = attrs.get("attribiutes", [])
        if "OTHER" in properties and not attrs.get("description"):
            raise serializers.ValidationError(
                {"description": "Opis jest wymagany, gdy wybrano 'Inne'."}
            )

        # Walidacja: jeden Review na użytkownika / parking_point
        user = self.context["request"].user
        parking_point = attrs.get("parking_point")
        if self.instance is None:  # tylko przy tworzeniu
            if Review.objects.filter(user=user, parking_point=parking_point).exists():
                raise serializers.ValidationError(
                    {
                        "detail": "Możesz dodać tylko jedną recenzję dla tego parking point."
                    }
                )

        return attrs
