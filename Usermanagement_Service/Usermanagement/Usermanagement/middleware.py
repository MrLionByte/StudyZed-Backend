# Usermanagment/middleware.py
from django.utils.deprecation import MiddlewareMixin
import time
from .metrics import http_requests_total, request_latency, normalize_endpoint

class PrometheusMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            # Calculate request duration
            duration = time.time() - request.start_time
            
            # Normalize the endpoint to avoid high cardinality
            endpoint = normalize_endpoint(request.path)
            
            # Track metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            request_latency.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
        return response