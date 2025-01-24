from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..models import ParkingPoint
from .serializers import ParkingPointSerializer


class ParkingPointViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla modelu ParkingPoint, który umożliwia pełne operacje CRUD.
    """

    queryset = ParkingPoint.objects.all()
    serializer_class = ParkingPointSerializer

    def perform_create(self, serializer):
        """
        Metoda pozwala dostosować zachowanie podczas tworzenia nowego obiektu.
        """
        serializer.save()
