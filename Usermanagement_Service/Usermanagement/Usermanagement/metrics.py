from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import re
from django.http import HttpResponse

http_requests_total = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'request_latency_seconds', 
    'Request latency in seconds',
    ['method', 'endpoint']
)

db_query_total = Counter(
    'db_query_total', 
    'Total database queries',
    ['query_type']
)

redis_operations_total = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation']
)

celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total number of Celery tasks',
    ['task_name', 'state']
)

celery_task_duration = Histogram(
    'celery_task_duration_seconds',
    'Duration of Celery tasks in seconds',
    ['task_name']
)

class TimerContextManager:
    def __init__(self, histogram, labels=None):
        self.histogram = histogram
        self.labels = labels
        self.start = None
        
    def __enter__(self):
        self.start = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.labels:
            self.histogram.labels(*self.labels).observe(time.time() - self.start)
        else:
            self.histogram.observe(time.time() - self.start)

def normalize_endpoint(path):
    path = re.sub(r'^/api/user-service/?', '', path)
    
    path = re.sub(r'/\d+', '/{id}', path)
    
    return path

def metrics_view(request):
    """View to expose Prometheus metrics."""
    return HttpResponse(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST
    )