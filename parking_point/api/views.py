from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..models import ParkingPoint
from .serializers import ParkingPointSerializer
from rest_framework.permissions import IsAuthenticated
from Reviews.models import Review
from Reviews.api.serializers import ReviewSerializer
from rest_framework.decorators import action
from parking_point_edit_location.models import ParkingPointEditLocation
from parking_point_edit_location.api.serializers import (
    ParkingPointEditLocationSerializer,
)
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.core.management import call_command
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from decouple import config


class ParkingPointViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla modelu ParkingPoint, który umożliwia pełne operacje CRUD.
    """

    queryset = ParkingPoint.objects.all()
    serializer_class = ParkingPointSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    # Walidacja create wykonywana jest w serializerze!!!
    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    def get_queryset(self):
        cutoff_date = timezone.now() - timedelta(days=30)
        return ParkingPoint.objects.annotate(
            like_count=Count("reviews", filter=Q(reviews__is_like=True)),
            dislike_count=Count("reviews", filter=Q(reviews__is_like=False)),
        ).filter(
            # LOGIKA WIDOCZNOŚCI:
            # Pokaż jeśli:
            # NIE jest oznaczony do usunięcia (stoper nie ruszył)
            # LUB stoper ruszył, ale było to mniej niż 30 dni temu
            Q(marked_for_deletion_at__isnull=True)
            | Q(marked_for_deletion_at__gt=cutoff_date)
        )


class CronDeleteExpiredPointsView(APIView):
    """
    Endpoint dla zewnętrznego crona (np. cron-job.org).
    Wymaga podania poprawnego klucza w parametrze ?secret=
    """
    permission_classes = [AllowAny] # Dostępny publicznie, ale zabezpieczony kluczem

    def get(self, request):
        secret = request.query_params.get("secret")
        expected_secret = config("CRON_SECRET_KEY", default="tajny-klucz-lokalny")

        if secret != expected_secret:
            return Response(
                {"detail": "Nieprawidłowy klucz autoryzacyjny."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Uruchamiamy komendę
            call_command("delete_expired_points")
            return Response(
                {"detail": "Komenda delete_expired_points wykonana pomyślnie."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Błąd podczas wykonywania komendy: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
