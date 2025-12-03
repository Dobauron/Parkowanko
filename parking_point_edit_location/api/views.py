from rest_framework import permissions, status
from rest_framework.response import Response
from django.db import IntegrityError
from ..models import ParkingPointEditLocation, ParkingPointEditLocationVote
from .serializers import ParkingPointEditLocationSerializer, ParkingPointEditLocationVoteSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView

class ParkingPointEditLocationView(GenericAPIView):
    serializer_class = ParkingPointEditLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        edit = ParkingPointEditLocation.objects.filter(parking_point_id=pk).first()
        if not edit:
            return Response({"edit": None})
        serializer = self.serializer_class(edit)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, parking_point_id=pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
#
# class ParkingPointEditLocationVoteViewSet(viewsets.ModelViewSet):
#     queryset = ParkingPointEditLocationVote.objects.all()
#     serializer_class = ParkingPointEditLocationVoteSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     http_method_names = ['get', 'post']