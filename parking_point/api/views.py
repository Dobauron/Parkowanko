from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..models import ParkingPoint
from .serializers import ParkingPointSerializer
from rest_framework.permissions import AllowAny
from Reviews.models import Review
from Reviews.api.serializers import ReviewSerializer
from rest_framework.decorators import action
from parking_point_edit_location.models import ParkingPointEditLocation
from parking_point_edit_location.api.serializers import (
    ParkingPointEditLocationSerializer,
)

from django.db.models import Count, Q


class ParkingPointViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla modelu ParkingPoint, który umożliwia pełne operacje CRUD.
    """

    queryset = ParkingPoint.objects.all()
    serializer_class = ParkingPointSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "post"]

    # Walidacja create wykonywana jest w serializerze!!!
    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    def get_queryset(self):
        return ParkingPoint.objects.annotate(
            like_count=Count("reviews", filter=Q(reviews__is_like=True)),
            dislike_count=Count(
                "reviews",
                filter=Q(reviews__is_like=False),
            ),
        )
