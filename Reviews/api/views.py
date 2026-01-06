from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from ..models import Review
from .serializers import ReviewSerializer
from parking_point.models import ParkingPoint


class ReviewCreateUpdateAPIView(GenericAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_parking_point(self):
        pk = self.kwargs.get("pk")
        if pk is None:
            raise ValidationError({"error": "Brak parking point ID."})
        return get_object_or_404(ParkingPoint, pk=pk)

    def get_user_review(self):
        return Review.objects.filter(
            user=self.request.user,
            parking_point=self.get_parking_point(),
        ).first()

    def get_serializer(self, *args, **kwargs):
        """
        Wymusza is_like=True, jeżeli użytkownik jest właścicielem parking point.
        """
        if self.request.method in ("POST", "PUT"):
            parking_point = self.get_parking_point()
            if parking_point.user_id == self.request.user.id:
                data = kwargs.get("data")
                if isinstance(data, dict):
                    data = data.copy()
                    data["is_like"] = True
                    kwargs["data"] = data

        return super().get_serializer(*args, **kwargs)

    @extend_schema(request=ReviewSerializer, responses=ReviewSerializer)
    def post(self, request, *args, **kwargs):
        """
        Tworzy recenzję. Jeśli już istnieje → 409.
        """
        if self.get_user_review():
            return Response(
                {"detail": "Recenzja już istnieje. Użyj PUT."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            parking_point=self.get_parking_point(),
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ReviewSerializer, responses=ReviewSerializer)
    def put(self, request, *args, **kwargs):
        """
        Aktualizuje recenzję. Jeśli nie istnieje → 404.
        """
        instance = self.get_user_review()
        if not instance:
            return Response(
                {"detail": "Recenzja nie istnieje. Użyj POST."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ParkingPointReviewsListAPIView(ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        parking_point = get_object_or_404(
            ParkingPoint, pk=self.kwargs["pk"]
        )

        return Review.objects.filter(
            parking_point=parking_point
        ).select_related("user")