from django.urls import path, include
from .views import ParkingPointEditLocationView

urlpatterns = [
    path(
        "",
        ParkingPointEditLocationView.as_view(),
        name="edit-location",
    ),
]
