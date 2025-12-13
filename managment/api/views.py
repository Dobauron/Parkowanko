from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.core.management import call_command
from django.conf import settings

from ..mock_data.seed import seed_all


class ResetDatabaseMockDataView(APIView):
    permission_classes = [permissions.IsAdminUser]  # tylko admin

    def post(self, request):
        if not settings.DEBUG:
            return Response(
                {"error": "Endpoint dostępny tylko w trybie DEBUG"},
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            # Flush bazy danych
            call_command("flush", interactive=False)
            # Migracje
            call_command("migrate")
            # Seedujemy mocki
            result = seed_all()

        return Response({
            "status": "success",
            "message": "Baza zresetowana i wypełniona mockami",
            "users_created": len(result["users"]),
            "parking_points_created": len(result["parking_points"]),
            "edit_locations_created": len(result["edit_locations"])
        }, status=status.HTTP_200_OK)
