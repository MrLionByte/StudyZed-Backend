from django.urls import path
from .views import get_chat_history, get_chatted_user, MessageFromTheHomePage

urlpatterns = [
    
    path('chatted-users/<str:user_code>/', get_chatted_user, name='chatted-users'),
    path('chat-history/<str:user_code>/<str:selected_user_code>/', get_chat_history, name='chat-history'),
    
    path('messages-to-admin/', MessageFromTheHomePage, name='messaging'),

]
