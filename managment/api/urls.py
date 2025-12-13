from django.urls import path
from .views import ResetDatabaseMockDataView

urlpatterns = [
    path("reset-mock-db/", ResetDatabaseMockDataView.as_view(), name="reset-mock-db"),
]
