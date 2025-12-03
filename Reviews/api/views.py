from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models import Review
from .serializers import ReviewSerializer
from django.db import IntegrityError
from rest_framework.generics import ListAPIView

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get","post","put"]

    def perform_create(self, serializer):
        user = self.request.user

        try:
            serializer.save(user=user)
        except IntegrityError:
            raise ValidationError(
                {"error": "Już zgłosiłeś to miejsce."}
            )


class ParkingPointReviewsList(ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(parking_point_id=self.kwargs["pk"])

