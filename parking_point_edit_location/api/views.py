from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from django.shortcuts import get_object_or_404
from parking_point.models import ParkingPoint
from .serializers import ParkingPointEditLocationSerializer


class ParkingPointEditLocationView(CreateAPIView):
    serializer_class = ParkingPointEditLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_parking_point(self):
        return get_object_or_404(ParkingPoint, pk=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
                "parking_point": self.get_parking_point(),
            },
        )
        serializer.is_valid(raise_exception=True)

        obj, created = serializer.upsert(serializer.validated_data)

        return Response(
            self.get_serializer(obj).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
