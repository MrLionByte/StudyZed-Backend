# Usermanagment/views.py
from django.http import HttpResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

def metrics_view(request):
    """
    View that exposes prometheus metrics
    """
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)