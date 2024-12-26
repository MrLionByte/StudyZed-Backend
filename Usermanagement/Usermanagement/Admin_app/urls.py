from django.urls import path
from .views import *


urlpatterns = [
    path('login-strict/', AdminBlockUserView.as_view(), name='admin_login'),
    
    path('admin/block-user/<int:pk>/', AdminBlockUserView.as_view(), name='admin_block_user'),
    
]
