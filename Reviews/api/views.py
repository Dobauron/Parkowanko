from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from parking_point.models import ParkingPoint
from ..models import Review
from .serializers import ReviewSerializer


# GET → lista recenzji punktu
# POST → dodanie recenzji
class ParkingPointReviewsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_parking_point(self):
        return get_object_or_404(ParkingPoint, pk=self.kwargs["pk"])

    def get_queryset(self):
        return Review.objects.filter(
            parking_point=self.get_parking_point()
        ).select_related("user")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["parking_point"] = self.get_parking_point()
        return context

    def perform_create(self, serializer):
        # blokada: 1 recenzja na usera
        if Review.objects.filter(
            user=self.request.user, parking_point_id=self.kwargs["pk"]
        ).exists():
            raise ValidationError("Już dodałeś recenzję dla tego punktu.")

        serializer.save(user=self.request.user, parking_point=self.get_parking_point())


# PUT → update po ID
class ReviewUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "review_id"

    def get_queryset(self):
        return Review.objects.filter(
            parking_point_id=self.kwargs["pk"], user=self.request.user
        )
