from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParkingPointReportViewSet

router = DefaultRouter()
router.register(r"", ParkingPointReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
]
