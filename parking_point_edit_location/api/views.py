from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from django.shortcuts import get_object_or_404
from parking_point.models import ParkingPoint
from ..models import ParkingPointEditLocation
from .serializers import ParkingPointEditLocationSerializer


class ParkingPointEditLocationView(CreateAPIView):
    serializer_class = ParkingPointEditLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_parking_point(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(ParkingPoint, pk=pk)

    #
    # --------- POST ----------
    #
    def post(self, request, *args, **kwargs):
        parking_point = self.get_parking_point()

        # Walidacja danych wejściowych
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "parking_point": parking_point},
        )
        serializer.is_valid(raise_exception=True)  # tu działają dekoratory

        # Nadpisanie lub stworzenie nowej propozycji
        obj, created = ParkingPointEditLocation.objects.update_or_create(
            user=request.user,
            parking_point=parking_point,
            defaults={"location": serializer.validated_data["location"]},
        )

        status_code = 201 if created else 200

        return Response(self.get_serializer(obj).data, status=status_code)
