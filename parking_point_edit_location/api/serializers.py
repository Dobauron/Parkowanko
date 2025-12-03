from rest_framework import serializers
from ..models import ParkingPointEditLocation, ParkingPointEditLocationVote

class ParkingPointEditLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingPointEditLocation
        fields = [
            "id",
            "user",
            "parking_point",
            "location",
            "created_at",
        ]
        read_only_fields = ["id", "user", "parking_point", "created_at"]

        def validate(self, attrs):
            user = self.context['request'].user
            parking_point_id = self.context['view'].kwargs.get('pk')

            if not ParkingPoint.objects.filter(pk=parking_point_id).exists():
                raise serializers.ValidationError({"parking_point": "Nie istnieje taki parking point."})

            if ParkingPointEditLocation.objects.filter(user=user, parking_point_id=parking_point_id).exists():
                raise serializers.ValidationError(
                    {"error": "Możesz zaproponować tylko jedną zmianę dla tego parking point."})

            return attrs

class ParkingPointEditLocationVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingPointEditLocationVote
        fields = "__all__"
        read_only_fields = ("id", "created_at", "user")