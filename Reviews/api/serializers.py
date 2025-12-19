from rest_framework import serializers
from ..models import Review
from .validators import (
    validate_attributes,
    validate_occupancy,
    validate_unique_review,
    validate_no_profanity,
)


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    attributes = serializers.ListField(
        child=serializers.CharField(validators=[validate_attributes]),
        required=False,
        allow_empty=True,
        default=list,
    )

    occupancy = serializers.CharField(
        validators=[validate_occupancy],
        required=True,
        allow_null=True,
        allow_blank=True,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[validate_no_profanity],
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "parking_point_id",
            "attributes",
            "occupancy",
            "description",
            "created_at",
            "is_like",
            "user"
        ]
        read_only_fields = ["id", "created_at", "parking_point_id"]

    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }

    @validate_unique_review
    def validate(self, attrs):
        return attrs
