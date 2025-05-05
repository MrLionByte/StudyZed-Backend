from django.urls import re_path, path
from .consumer import ChatConsumer, PersonalChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_code>[\w-]+)/$', ChatConsumer.as_asgi()),
    path('ws/chat/<int:id>/', PersonalChatConsumer.as_asgi()),
]