from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OneToOneLiveVideoViewSet

router = DefaultRouter()
router.register(r'individual-live-sessions', OneToOneLiveVideoViewSet, basename='individual-live-session')

urlpatterns = [
    path('', include(router.urls)),
]