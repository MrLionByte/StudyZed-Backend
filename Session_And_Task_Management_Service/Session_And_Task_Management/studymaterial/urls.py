from django.urls import path
from .views import * 


urlpatterns = [

    path('add-notes/', AddStudyMaterialViews.as_view()),
    path('get-notes/',GetStudyMaterialViews.as_view()),
    
]