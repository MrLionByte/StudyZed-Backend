from .views import *
from django.urls import path

urlpatterns = [

    path('get-all-subscriptions-amount/', GetAllSubscriptionAmountsView.as_view()),
    path("update-amount/<str:pk>/", ChangeSubscriptionAmountView.as_view()),

]
