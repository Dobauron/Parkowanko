from rest_framework import serializers
from ..models import Review
from .validators import (
    validate_attributes,
    validate_occupancy,
    validate_no_profanity,
)
from django.db import transaction


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
            "created_at",
            "is_like",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }

    def upsert(self, validated_data):
        user = self.context["request"].user
        parking_point = self.context["parking_point"]

        obj, created = Review.objects.update_or_create(
            user=user,
            parking_point=parking_point,
            defaults=validated_data,
        )
        return obj, created