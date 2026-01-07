from django.urls import path
from .views import (
    ReviewCreateUpdateAPIView,
    ParkingPointReviewsListAPIView,
)

urlpatterns = [
    # GET → lista recenzji punktu
    path("", ParkingPointReviewsListAPIView.as_view(), name="reviews-list"),
    # POST, PUT → moja recenzja dla punktu
    path("me/", ReviewCreateUpdateAPIView.as_view(), name="my-review"),
]
