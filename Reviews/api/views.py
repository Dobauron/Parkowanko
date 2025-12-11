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
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_parking_point(self):
        """
        Pobiera parking point na podstawie pk z URL.
        Zwraca None podczas generowania schematu (drf-spectacular),
        gdzie pk nie jest dostępne.
        """
        pk = self.kwargs.get("pk")
        if pk is None:
            return None  # dla schema generatora
        return get_object_or_404(ParkingPoint, pk=pk)

    def get_queryset(self):
        """
        GET bez PK → np. podczas generowania OpenAPI → zwracamy queryset pusty,
        aby uniknąć błędów 404.
        """
        pk = self.kwargs.get("pk")
        if pk is None:
            return Review.objects.none()  # dla dokumentacji

        return Review.objects.filter(parking_point_id=pk)

    def get_serializer(self, *args, **kwargs):
        """
        Wstrzykuje is_like=True dla twórcy parking pointa
        BEFORE walidacja.
        """
        if self.request.method == "POST":
            parking_point = self.get_parking_point()

            if parking_point and parking_point.user_id == self.request.user.id:
                data = kwargs.get("data")
                if isinstance(data, dict):
                    # Nie zmieniamy request.data! Modyfikujemy kopię.
                    data = data.copy()
                    data["is_like"] = True
                    kwargs["data"] = data

        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        parking_point = self.get_parking_point()
        if parking_point is None:
            raise ValidationError({"error": "Brak obiektu parking point."})

        user = self.request.user
        try:
            serializer.save(user=user, parking_point=parking_point)
        except IntegrityError:
            raise ValidationError({"error": "Już zgłosiłeś to miejsce."})

