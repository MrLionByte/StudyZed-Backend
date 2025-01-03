from django.urls import path
from .views import *


urlpatterns = [
    
    path('login-strict/', AdminLoginView.as_view(), name='admin_login'),
    path('tutor-management/', AdminAllTutorsListView.as_view(), name='admin_manage_tutors'),
    path('student-management/', AdminAllStudentsListView.as_view(), name='admin_manage_students'),
    
    path('block-user/<int:pk>/', AdminBlockUserView.as_view(), name='admin_block_user'),
    
]
