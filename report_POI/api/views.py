from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models import ParkingPointReport
from .serializers import ParkingPointReportSerializer
from django.db import IntegrityError


class ParkingPointReportViewSet(viewsets.ModelViewSet):
    queryset = ParkingPointReport.objects.all()
    serializer_class = ParkingPointReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()  # Kopiujemy dane, aby je modyfikować
        data["user"] = (
            user.id
        )  # Dodajemy usera do danych (jest read_only, więc nie może być edytowalny)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)  # 🚀 Walidacja serializera!
        try:
            report = serializer.save(
                user=user
            )  # Tworzymy obiekt przez serializer (wywoła `validate`!)
        except IntegrityError:
            return Response(
                {"error": "Już zgłosiłeś to miejsce. "},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sprawdzenie, czy trzeba usunąć parking
        report.parking_point.check_and_delete()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )  # Automatycznie przypisujemy użytkownika
