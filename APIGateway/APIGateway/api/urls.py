from django.urls import path, re_path
from .views import APIgateView

urlpatterns = [
    path("<service>/<path:path>", APIgateView.as_view(), name="api_gateway"),
]
