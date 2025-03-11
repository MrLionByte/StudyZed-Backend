"""
URL configuration for Session_And_Task_Management project.

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

urlpatterns = [
    
    path("admin/", admin.site.urls),
    
    path('session-tutor/', include('session_tutor.urls')),
    path('assessment-tutor/', include('assessment_tutor_side.urls')),
    path('task-tutor/', include('task_tutor_side.urls')),
    
    path('session-student/', include('students_in_session.urls')),
    path('assessment-student/', include('assessment_student_side.urls')),
    path('task-student/', include('task_student_side.urls')),
    
    path('progress/', include('progress.urls')),
    path('student-progress/', include('progress_Student_side.urls')),
    
    path('study-material/', include('studymaterial.urls')),
    
    path('dashboard-tutor/', include('dashboard_tutor.urls')),
    path('dashboard-student/', include('dashboard_student.urls')),
    
    path('session-admin/', include('admin_app.urls')),
    
]
