from rest_framework import serializers
from ..models import Review
from .validators import (
    validate_attributes,
    validate_occupancy,
    validate_no_profanity,
)
from drf_spectacular.utils import extend_schema_field


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    parking_point_id = serializers.IntegerField(
        source="parking_point.id", read_only=True
    )

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
            "is_like",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(serializers.DictField)
    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }
