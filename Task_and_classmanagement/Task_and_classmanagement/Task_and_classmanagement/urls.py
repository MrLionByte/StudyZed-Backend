"""
URL configuration for Task_and_classmanagement project.

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
# from class_management.class_teacher import urls
# from class_management.class_student import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('class_teacher', include('class_management.class_teacher.urls')),
    path('class_student', include('class_management.class_student.urls')),
    path('class_admin', include('class_management.class_admin.urls')),
    
]
