from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ParkingPointViewSet

# Tworzymy router i rejestrujemy nasz ViewSet
router = SimpleRouter()
router.register(r"", ParkingPointViewSet, basename="parking-point")

urlpatterns = router.urls