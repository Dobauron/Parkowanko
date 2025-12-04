from rest_framework import permissions, status
from rest_framework.response import Response
from django.db import IntegrityError
from ..models import ParkingPointEditLocation, ParkingPointEditLocationVote
from .serializers import ParkingPointEditLocationSerializer, ParkingPointEditLocationVoteSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from parking_point.models import ParkingPoint
from django.shortcuts import get_object_or_404

class ParkingPointEditLocationView(CreateAPIView):
    serializer_class = ParkingPointEditLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_parking_point(self):
        """Pobiera parking point na podstawie pk z URL"""
        pk = self.kwargs.get('pk')
        return get_object_or_404(ParkingPoint, pk=pk)

    def get(self, request, *args, **kwargs):
        """
        GET: Sprawdza czy użytkownik ma już propozycję edycji
        """
        parking_point = self.get_parking_point()

        try:
            edit_location = ParkingPointEditLocation.objects.get(
                user=request.user,
                parking_point=parking_point
            )
            serializer = self.get_serializer(edit_location)

            return Response({
                "has_proposal": True,
                "proposal": serializer.data,
                "created_at": edit_location.created_at,
                "parking_point_id": parking_point.id
            }, status=status.HTTP_200_OK)

        except ParkingPointEditLocation.DoesNotExist:
            return Response({
                "has_proposal": False,
                "message": "Nie masz jeszcze propozycji edycji dla tego punktu.",
                "parking_point_id": parking_point.id,
                "current_location": parking_point.location
            }, status=status.HTTP_200_OK)  # 200 zamiast 404, bo to nie jest błąd

    def post(self, request, *args, **kwargs):
        """
        POST: Tworzy nową propozycję edycji lokalizacji
        """
        parking_point = self.get_parking_point()

        serializer = self.get_serializer(
            data=request.data,
            context={
                'request': request,
                'parking_point': parking_point
            }
        )
        serializer.is_valid(raise_exception=True)

        # Użyj perform_create aby automatycznie dodać user i parking_point
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        """Dodaje user i parking_point przed zapisem"""
        serializer.save(
            user=self.request.user,
            parking_point=self.get_parking_point()
        )
#
# class ParkingPointEditLocationVoteViewSet(viewsets.ModelViewSet):
#     queryset = ParkingPointEditLocationVote.objects.all()
#     serializer_class = ParkingPointEditLocationVoteSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     http_method_names = ['get', 'post']