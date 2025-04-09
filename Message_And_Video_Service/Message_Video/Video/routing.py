from django.urls import re_path, path
from .consumer import VideoCallConsumer, LiveSessionOneToOneConsumer


websocket_urlpatterns = [
    re_path(
        r'ws/video-group/(?P<room_id>[\w-]+)/$', VideoCallConsumer.as_asgi()
        ),

    re_path(r'ws/video-one-on-one/(?P<receiver>[\w-]+)/$', LiveSessionOneToOneConsumer.as_asgi()),
]
print("Web Sockrt Url :", websocket_urlpatterns)