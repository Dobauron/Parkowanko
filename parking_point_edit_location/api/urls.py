from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParkingPointEditLocationView

urlpatterns = [
    path('<int:pk>/edit-location/', ParkingPointEditLocationView.as_view(), name='edit-location'),
]