"""
URL configuration for Usermanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .health_check import health_check_action
from .metrics import metrics_view
from AuthApp import urls
from UserApp import urls
from Admin_app import urls


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('auth-app/', include('AuthApp.urls')),
    path('user-app/', include('UserApp.urls')),
    path('class-app/', include('Class_app.urls')),
    path('admin-app/', include('Admin_app.urls')),
    path("healthz/", health_check_action, name="healthz"),
    path("metrics/", metrics_view, name="prometheus-metrics"),
    
    # path('silk/', include('silk.urls', namespace='silk')),
]
