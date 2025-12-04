from rest_framework.routers import DefaultRouter
from .views import ParkingPointViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"", ParkingPointViewSet, basename="parkingpoint")

urlpatterns = [
    path("", include(router.urls)),
]
