from rest_framework import permissions, status
from rest_framework.response import Response
from ..models import Review
from .serializers import ReviewSerializer
from django.db import IntegrityError
from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from parking_point.models import ParkingPoint


class ReviewAPICreateListView(ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_parking_point(self):
        """Pobiera parking point na podstawie pk z URL"""
        pk = self.kwargs.get("pk")
        return get_object_or_404(ParkingPoint, pk=pk)

    def get_queryset(self):
        return Review.objects.filter(parking_point_id=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        self.get_parking_point()
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        parking_point = self.get_parking_point()
        try:
            serializer.save(user=user, parking_point=parking_point)
        except IntegrityError:
            raise ValidationError({"error": "Już zgłosiłeś to miejsce."})
