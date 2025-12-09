from rest_framework.routers import DefaultRouter
from .views import ParkingPointViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"", ParkingPointViewSet, basename="parkingpoint")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/reviews/", include("Reviews.api.urls")),
    path("<int:pk>/edit-location/", include("parking_point_edit_location.api.urls")),
]
