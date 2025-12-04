from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParkingPointEditLocationView, ParkingPointEditLocationVoteView

urlpatterns = [
    path(
        "<int:pk>/edit-location/",
        ParkingPointEditLocationView.as_view(),
        name="edit-location",
    ),
    path(
        "<int:pk>/edit-location/vote/",
        ParkingPointEditLocationVoteView.as_view(),
        name="edit-location-vote",
    ),
]
