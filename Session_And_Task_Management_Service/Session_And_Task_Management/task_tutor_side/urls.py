from django.urls import path
from .views import * 


urlpatterns = [

    path('create-new-task/', CreateNewTaskView.as_view()),
    path('get-all-tasks/', GetAllTasksView.as_view()),
    path('edit-task/<int:task_id>/',EditTaskView.as_view()),
    path('tasks/<int:pk>/mark/', GiveMarkForDailyTaskView.as_view()),

]