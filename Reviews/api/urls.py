from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewAPICreateListView


urlpatterns = [
    path("", ReviewAPICreateListView.as_view(), name="review"),
]
