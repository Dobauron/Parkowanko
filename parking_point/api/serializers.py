from rest_framework import serializers
from ..models import ParkingPoint


class ParkingPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingPoint
        fields = "__all__"
