from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import connection, transaction
from django.core.management import call_command
from django.conf import settings
from rest_framework.permissions import IsAdminUser, AllowAny
from ..mock_data.seed import seed_all
from drf_spectacular.utils import extend_schema  # Importuj jeśli używasz Swaggera


class ResetDatabaseMockDataView(APIView):
    permission_classes = [permissions.AllowAny]
    # Dodanie tej linii uciszy błąd o "unable to guess serializer"
    serializer_class = None

    @extend_schema(
        responses={200: None}, description="Resetuje całą bazę i wgrywa mocki."
    )
    def post(self, request):
        # Na Renderze settings.DEBUG może być False!
        # Upewnij się, że masz to ustawione w zmiennych środowiskowych Rendera.
        if not settings.DEBUG:
            return Response(
                {"error": "Endpoint dostępny tylko w trybie DEBUG"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Render korzysta z Postgresa, więc to zadziała
                    cursor.execute("DROP SCHEMA public CASCADE;")
                    cursor.execute("CREATE SCHEMA public;")
                    cursor.execute(
                        "GRANT ALL ON SCHEMA public TO public;"
                    )  # Czasem wymagane uprawnienia

                # Odpalamy migracje na świeżym schemacie
                call_command("migrate", interactive=False)

                # Seedujemy dane
                result = seed_all()

            return Response(
                {
                    "status": "success",
                    "message": "Baza zresetowana i wypełniona mockami",
                    "users_created": len(result["users"]),
                    "parking_points_created": len(result["parking_points"]),
                    "edit_locations_created": len(result["edit_locations"]),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            # Warto wiedzieć, co dokładnie wybuchło
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
