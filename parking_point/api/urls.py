from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParkingPointViewSet

# Tworzymy router i rejestrujemy nasz ViewSet
router = DefaultRouter()
router.register(r"parking-points", ParkingPointViewSet, basename="parking-point")

urlpatterns = [
    path("", include(router.urls)),
]
