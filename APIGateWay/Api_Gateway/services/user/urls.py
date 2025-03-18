from django.urls import path
from .views import AdminViews, AuthViews, ClassViews, UserViews

app_name = 'user_management'

urlpatterns = [
    path('auth-app/<path:path>', AuthViews.UserAuthAppView.as_view(), name='auth-app'),
    # path('user-app/<path:path>', UserViews.as_view(), name='user-app'),
    # path('class-app/<path:path>', ClassViews.as_view(), name='class-app'),
    # path('admin-app/<path:path>', AdminViews.as_view(), name='admin-app'),
]