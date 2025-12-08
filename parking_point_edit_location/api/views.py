from rest_framework import permissions, status
from rest_framework.response import Response
from django.db import IntegrityError
from ..models import ParkingPointEditLocation, ParkingPointEditLocationVote
from .serializers import (
    ParkingPointEditLocationSerializer,
    ParkingPointEditLocationVoteSerializer,
)
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from parking_point.models import ParkingPoint
from django.shortcuts import get_object_or_404


class ParkingPointEditLocationView(CreateAPIView):
    serializer_class = ParkingPointEditLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_parking_point(self):
        """Pobiera parking point na podstawie pk z URL"""
        pk = self.kwargs.get("pk")
        return get_object_or_404(ParkingPoint, pk=pk)

    def get(self, request, *args, **kwargs):
        """
        GET: Sprawdza czy użytkownik ma już propozycję edycji
        """
        parking_point = self.get_parking_point()

        try:
            edit_location = ParkingPointEditLocation.objects.get(
                parking_point=parking_point
            )
            serializer = self.get_serializer(edit_location)

            return Response(
                {
                    "has_proposal": True,
                    "proposal": serializer.data,
                    "created_at": edit_location.created_at,
                    "parking_point_id": parking_point.id,
                },
                status=status.HTTP_200_OK,
            )

        except ParkingPointEditLocation.DoesNotExist:
            return Response(
                {
                    "has_proposal": False,
                    "message": "Nie masz jeszcze propozycji edycji dla tego punktu.",
                    "parking_point_id": parking_point.id,
                    "current_location": parking_point.location,
                },
                status=status.HTTP_200_OK,
            )  # 200 zamiast 404, bo to nie jest błąd

    def post(self, request, *args, **kwargs):
        """
        POST: Tworzy nową propozycję edycji lokalizacji
        """
        parking_point = self.get_parking_point()

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "parking_point": parking_point},
        )
        serializer.is_valid(raise_exception=True)

        # Użyj perform_create aby automatycznie dodać user i parking_point
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        """Dodaje user i parking_point przed zapisem"""
        parking_point = self.get_parking_point()
        # Zapis propozycji
        edit_location = serializer.save(
            user=self.request.user, parking_point=parking_point
        )

        # Tworzymy automatycznie vote z is_like=None
        ParkingPointEditLocationVote.objects.create(
            user=self.request.user,
            parking_point_edit_location=edit_location,
            is_like=None,
        )


class ParkingPointEditLocationVoteView(CreateAPIView):
    """
    Głosowanie na AKTYWNĄ propozycję dla danego ParkingPoint
    POST /api/parking-points/<int:pk>/edit-location/vote/
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ParkingPointEditLocationVoteSerializer

    def get_serializer_context(self):
        """
        metoda która zwraca słownik danych dostępnych w serializerze jako self.context.
        """
        context = super().get_serializer_context()
        context["parking_point_id"] = self.kwargs["pk"]
        proposal = ParkingPointEditLocation.objects.filter(
            parking_point_id=self.kwargs["pk"]
        ).first()

        if proposal:
            context["proposal"] = proposal  # <-- PRZYPISANIE!

        context["parking_point_id"] = self.kwargs["pk"]
        context["method"] = self.request.method
        return context

    def perform_create(self, serializer):
        """
        CreateAPIView automatycznie wywoła tę metodę po walidacji.
        Tu przekazujemy user i proposal do save().
        """
        # 1. Znajdź proposal (walidator już go znalazł i zapisał w context)
        proposal = serializer.context.get("proposal")

        if not proposal:
            # Jeśli walidator nie dodał, znajdź sam
            parking_point_id = self.kwargs["pk"]
            proposal = ParkingPointEditLocation.objects.filter(
                parking_point_id=parking_point_id
            ).first()

            if not proposal:
                raise serializers.ValidationError("Nie znaleziono propozycji.")

        # 2. DRF-way: przekaż dodatkowe pola do save()
        serializer.save(user=self.request.user, parking_point_edit_location=proposal)

    def put(self, request, pk):
        proposal = get_object_or_404(ParkingPointEditLocation, parking_point_id=pk)

        vote = get_object_or_404(
            ParkingPointEditLocationVote,
            parking_point_edit_location=proposal,
            user=request.user,
        )

        serializer = ParkingPointEditLocationVoteSerializer(
            vote, data=request.data, partial=True, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        vote.is_like = serializer.validated_data["is_like"]
        vote.save(update_fields=["is_like"])

        return Response({"message": "Głos zaktualizowany."}, status=200)
