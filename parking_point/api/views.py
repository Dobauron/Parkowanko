from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..models import ParkingPoint
from .serializers import ParkingPointSerializer
from rest_framework.permissions import AllowAny
from Reviews.models import Review
from Reviews.api.serializers import ReviewSerializer
from rest_framework.decorators import action
from parking_point_edit_location.models import (
    ParkingPointEditLocation,
    ParkingPointEditLocationVote,
)
from parking_point_edit_location.api.serializers import (
    ParkingPointEditLocationSerializer,
    ParkingPointEditLocationVoteSerializer,
)


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

    @action(detail=True, methods=["get"], url_path="reviews")
    def reviews(self, request, pk=None):
        """
        GET /api/parking-points/{id}/reviews/
        """
        reviews = Review.objects.filter(parking_point_id=pk)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    # @action(
    #     detail=True,
    #     methods=["get", "post"],
    #     url_path="edit-location",
    #     serializer_class=ParkingPointEditLocationSerializer,
    # )
    # def edit_location(self, request, pk=None):
    #     """
    #     GET  /api/parking-points/{id}/edit-location/
    #     POST /api/parking-points/{id}/edit-location/
    #     """
    #
    #     if request.method == "GET":
    #         edit = ParkingPointEditLocation.objects.filter(parking_point_id=pk).first()
    #         if not edit:
    #             return Response({"edit": None})
    #         serializer = ParkingPointEditLocationSerializer(edit)
    #         return Response(serializer.data)
    #
    #     if request.method == "POST":
    #         data = request.data.copy()
    #
    #         serializer = ParkingPointEditLocationSerializer(data=data, context={"request": request, "view": self})
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(
    #             user=request.user,
    #             parking_point_id=pk
    #         )
    #
    #         return Response(serializer.data, status=201)
    #
    #
    # @action(detail=True, methods=["get", "post"], url_path="edit-location/votes")
    # def edit_location_votes(self, request, pk=None):
    #     """
    #     Endpoint do głosowania nad propozycją edycji.
    #     """
    #     # pk = parking_point.id
    #     edit = ParkingPointEditLocation.objects.filter(parking_point_id=pk).first()
    #     if not edit:
    #         return Response({"detail": "Brak propozycji edycji"}, status=404)
    #
    #     if request.method == "GET":
    #         votes = edit.votes.all()
    #         serializer = ParkingPointEditLocationVoteSerializer(votes, many=True)
    #         return Response(serializer.data)
    #
    #     if request.method == "POST":
    #         data = request.data.copy()
    #         data["edit"] = edit.id
    #         serializer = ParkingPointEditLocationVoteSerializer(data=data, context={'request': request})
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=201)
