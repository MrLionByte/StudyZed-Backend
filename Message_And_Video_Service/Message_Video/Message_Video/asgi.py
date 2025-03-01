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
from Chat.routing import websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator
from Chat.channels_middleware  import JWTForWebsocketMiddleware


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Message_Video.settings")

# django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTForWebsocketMiddleware(AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        ))
    )
})

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     'websocket': URLRouter(websocket_urlpatterns),
# })

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator
#         # (
#         # AuthMiddlewareStack(
#         #     URLRouter(
#         #         websocket_urlpatterns
#         #     )
#         # )
#         # ),
#         (
#             URLRouter(
#                 websocket_urlpatterns
#             )
#         )
# })