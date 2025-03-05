"""
ASGI config for Message_Video project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from Chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from Video.routing import websocket_urlpatterns as video_websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator
from Chat.channels_middleware  import JWTForWebsocketMiddleware as ChatWebsocketMiddleware
from Video.channels_middleware import JWTForWebRTCMiddleware as VideoWebRTCMiddleWare

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Message_Video.settings")

django_asgi_app = get_asgi_application()

websocket_urlpatterns = (
    chat_websocket_urlpatterns + video_websocket_urlpatterns
)

class CustomWebSocketMiddleWare:
    """
    MiddleWare for different JWT authentication middleware based on the WebSocket path. 
    """
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        path = scope['path']
        
        if path.startswith('/ws/chat/'):
            middleware = ChatWebsocketMiddleware(self.inner)
            return await middleware(scope, receive, send) 
        elif path.startswith('/ws/video/') or path.startswith('/ws/video-one-on-one/'):
            middleware = VideoWebRTCMiddleWare(self.inner)
            return await middleware(scope, receive, send) 
        return await self.inner(scope, receive, send) 
    

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        CustomWebSocketMiddleWare
            (AuthMiddlewareStack(
                URLRouter(
                    websocket_urlpatterns
                    )
                )
            )
        )
})