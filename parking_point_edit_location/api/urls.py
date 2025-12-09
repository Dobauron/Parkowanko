from django.urls import path, include
from .views import ParkingPointEditLocationView, ParkingPointEditLocationVoteView

urlpatterns = [
    path(
        "",
        ParkingPointEditLocationView.as_view(),
        name="edit-location",
    ),
    path(
        "vote/",
        ParkingPointEditLocationVoteView.as_view(),
        name="edit-location-vote",
    ),
]
