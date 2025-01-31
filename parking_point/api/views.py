from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..models import ParkingPoint
from .serializers import ParkingPointSerializer
from .validators import validate_location
from rest_framework.permissions import AllowAny


class ParkingPointViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla modelu ParkingPoint, który umożliwia pełne operacje CRUD.
    """

    queryset = ParkingPoint.objects.all()
    serializer_class = ParkingPointSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Pobierz dane do aktualizacji
        data = request.data
        try:
            new_lat = float(data["location"]["lat"])
            new_lng = float(data["location"]["lng"])
        except (KeyError, ValueError):
            raise ValidationError(
                "Nieprawidłowe dane lokalizacji: 'lat' i 'lng' muszą być liczbami."
            )

        # Walidacja lokalizacji: max_distance=1000 dla sprawdzenia odległości od obecnej pozycji
        validate_location(new_lat, new_lng, exclude_id=instance.id, max_distance=1000)

        # Aktualizacja instancji
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
