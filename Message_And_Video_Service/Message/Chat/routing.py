from django.urls import re_path, path
from .consumer import ChatConsumer, PersonalChatConsumer

# websocket_urlpatterns = [
#     re_path(r'ws/chat/(?P<chat_id>\w+)/$', ChatConsumer.as_asgi()),
# ]

# websocket_urlpatterns = [
#     path('ws/chat/<str:userID>/', ChatConsumer.as_asgi(),)
# ]


websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<id>[\w-]+)/$', ChatConsumer.as_asgi()),
    path('ws/chat/<str:user_code>/', ChatConsumer.as_asgi()),
    path('ws/chat/<int:id>/', PersonalChatConsumer.as_asgi()),
]