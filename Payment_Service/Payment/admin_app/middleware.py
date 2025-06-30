import logging
from django.core.exceptions import DisallowedHost

logger = logging.getLogger(__name__)

class NormalizeHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get('HTTP_HOST', '')
        if ':' in host:
            host = host.split(':')[0]
        if host == 'payment_management':
            host = host.replace('_', '-')
        request.META['HTTP_HOST'] = host
        logger.debug(f"Normalized HTTP_HOST: {host}")
        try:
            request.get_host()
        except DisallowedHost as e:
            logger.error(f"Host validation failed: {e}")
            raise
        return self.get_response(request)