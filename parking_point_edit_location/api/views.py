from rest_framework import permissions, status
from rest_framework.response import Response
from django.db import IntegrityError
from ..models import ParkingPointEditLocation
from .serializers import ParkingPointEditLocationSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from parking_point.models import ParkingPoint
from django.shortcuts import get_object_or_404


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

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "parking_point": parking_point},
        )
        serializer.is_valid(raise_exception=True)

        obj = serializer.save(user=request.user, parking_point=parking_point)

        # Tworzymy automatycznie vote z is_like=None
        ParkingPointEditLocationVote.objects.create(
            user=request.user,
            parking_point_edit_location=obj,
            is_like=None,
        )

        # Zwracamy te same dane co GET
        return Response(self.get_serializer(obj).data, status=201)



