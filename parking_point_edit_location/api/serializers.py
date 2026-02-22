from rest_framework import serializers
from ..models import ParkingPointEditLocation
from drf_spectacular.utils import extend_schema_field
from parking_point.api.serializers import LatLngField # Importujemy nasze pole

class ParkingPointEditLocationSerializer(serializers.ModelSerializer):
    parkingPointId = serializers.IntegerField(source="parking_point.id", read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    location = LatLngField() # Używamy LatLngField

    class Meta:
        model = ParkingPointEditLocation
        fields = [
            "id",
            "location",
            "parkingPointId",
            "user",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.DictField)
    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "username": obj.user.username,
        }

    def upsert(self, validated_data):
        user = self.context["request"].user
        parking_point = self.context["parking_point"]

        obj, created = ParkingPointEditLocation.objects.update_or_create(
            user=user,
            parking_point=parking_point,
            defaults={"location": validated_data["location"]},
        )
        return obj, created
