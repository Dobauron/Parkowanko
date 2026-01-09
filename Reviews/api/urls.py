from django.urls import path
from .views import (
    ParkingPointReviewsListCreateAPIView,
    ReviewUpdateAPIView,
)

urlpatterns = [
    path(
        "", ParkingPointReviewsListCreateAPIView.as_view(), name="reviews-list-create"
    ),
    path("<int:review_id>/", ReviewUpdateAPIView.as_view(), name="review-update"),
]
